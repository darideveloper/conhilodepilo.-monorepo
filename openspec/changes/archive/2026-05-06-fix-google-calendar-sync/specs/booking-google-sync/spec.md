## MODIFIED Requirements

### Requirement: Automatic Sync via Django Signals
The system MUST automatically sync `Booking` changes to Google Calendar via Django signals registered in `dashboard/booking/signals.py` and connected in `BookingConfig.ready()`. All sync invocations MUST be deferred via `transaction.on_commit(...)` so they only fire after the surrounding DB transaction commits.

The signal layer MUST:
- On `m2m_changed` of `Booking.services` (actions `post_add`, `post_remove`, `post_clear`): recalculate `end_time`, save with `update_fields=["end_time"]`, then schedule `sync_booking_to_google` for the booking when `instance.status != "PENDING"` and at least one service is attached.
- On `post_save`:
  - Skip when `update_fields` is a subset of `{google_event_id, google_sync_status, google_sync_error, last_synced_at, end_time}`. (`end_time` is added so the `m2m_changed` handler's `save(update_fields=["end_time"])` and `Booking.save()`'s automatic `end_time` recomputation do NOT trigger a second sync — the m2m handler is the sync trigger when services/end_time change.)
  - Skip when `instance.status == "PENDING"` (pre-paid bookings wait for Stripe webhook).
  - Otherwise, schedule `sync_booking_to_google` via `transaction.on_commit`.
- On `post_delete`: schedule `delete_google_calendar_event` via `transaction.on_commit`.

The handler MUST NOT depend on `created=True` being skipped — explicit sync calls from `CreateBookingView` and the m2m_changed handler are the source of truth for new-booking sync.

#### Scenario: Booking created from API with services attached
- **WHEN** `CreateBookingView` creates a CONFIRMED booking and calls `services.set([...])`
- **THEN** exactly one `events().insert` call is made after the DB transaction commits
- **AND** the new `google_event_id` is persisted

#### Scenario: Booking created from admin
- **WHEN** a new booking is saved via the Django admin and services are attached
- **THEN** the `m2m_changed` handler schedules sync via `transaction.on_commit`
- **AND** exactly one `events().insert` call is made after commit

#### Scenario: Booking status updated from admin
- **WHEN** an admin changes a booking's status (e.g., PENDING → CONFIRMED) and saves
- **THEN** the corresponding Google Calendar event is patched with updated data after commit

#### Scenario: Booking deleted from admin
- **WHEN** a booking is deleted from the Django admin
- **THEN** `post_delete` fires and the corresponding Google Calendar event is removed after commit

#### Scenario: Internal sync field updates do not re-trigger sync
- **WHEN** `sync_booking_to_google` writes back `google_event_id`, `google_sync_status`, `google_sync_error`, or `last_synced_at`
- **THEN** the resulting `post_save` is skipped because `update_fields` is a subset of the internal Google fields

#### Scenario: end_time recomputation does not re-trigger sync
- **WHEN** the `m2m_changed` handler saves with `update_fields=["end_time"]`, or `Booking.save()` recomputes `end_time` and saves with `update_fields={"start_time", "end_time"}`
- **THEN** the resulting `post_save` is skipped (m2m_changed is the sole sync trigger for service/time-driven changes)

#### Scenario: PENDING booking does not sync
- **WHEN** a booking with `status="PENDING"` is created or saved
- **THEN** no calendar API call is made

## ADDED Requirements

### Requirement: Cancelled Booking Visual Marker
When a booking transitions to `status="CANCELLED"` and has a non-null `google_event_id`, the system MUST patch the existing event so its `summary` is prefixed with `"[CANCELLED] "`. The event MUST remain on the calendar (not deleted) so it serves as a historical record. The `google_event_id` MUST be retained.

The prefix MUST be idempotent: if the summary already starts with `"[CANCELLED] "`, the system MUST NOT add a second prefix.

#### Scenario: Active booking is cancelled
- **GIVEN** a booking with `status="CONFIRMED"` and `google_event_id="abc123"`
- **WHEN** the booking is updated to `status="CANCELLED"` and saved
- **THEN** `events().patch(eventId="abc123")` is called after commit
- **AND** the patched `summary` starts with `"[CANCELLED] "`
- **AND** `booking.google_event_id` remains `"abc123"`

#### Scenario: Re-saving an already cancelled booking does not double-prefix
- **GIVEN** a cancelled booking whose calendar event summary is `"[CANCELLED] Maria — Lash Lift"`
- **WHEN** the booking is saved again
- **THEN** the patched summary is `"[CANCELLED] Maria — Lash Lift"` (unchanged)

#### Scenario: Cancelled booking is hard-deleted
- **GIVEN** a cancelled booking with `google_event_id="abc123"`
- **WHEN** `booking.delete()` is called
- **THEN** `events().delete(eventId="abc123")` is invoked after commit

### Requirement: Pre-paid Booking Deferred Sync
Bookings that require pre-payment (status `"PENDING"`) MUST NOT be synced to Google Calendar until payment is confirmed. The Stripe webhook handler transitions the booking to `"PAID"` via `booking.save(update_fields=["status", "stripe_payment_id"])`, which triggers `post_save` and the deferred sync.

#### Scenario: Pre-paid booking creation triggers no API call
- **WHEN** a new booking is created with `status="PENDING"` and services attached
- **THEN** no Google Calendar API call is made

#### Scenario: Stripe webhook completes pre-paid booking
- **GIVEN** a PENDING booking
- **WHEN** the Stripe webhook delivers `checkout.session.completed` and the handler sets `status="PAID"` and saves
- **THEN** exactly one `events().insert` call is made after the webhook handler returns

### Requirement: Explicit Sync on API Creation
`CreateBookingView.post` MUST explicitly schedule `sync_booking_to_google(booking)` via `transaction.on_commit` after `booking.services.set(services)` when the booking's status is `"CONFIRMED"`. The view MUST NOT rely on the m2m_changed side-effect alone.

The booking creation MUST be wrapped in `transaction.atomic()` so `transaction.on_commit` has well-defined behavior.

#### Scenario: API creates a CONFIRMED booking
- **WHEN** `CreateBookingView` creates a booking with status `"CONFIRMED"` and attaches services
- **THEN** `sync_booking_to_google` is scheduled exactly once via `transaction.on_commit`
- **AND** the call fires after the response is returned (or at transaction commit)

#### Scenario: API creates a PENDING (pre-paid) booking
- **WHEN** `CreateBookingView` creates a booking with status `"PENDING"`
- **THEN** `sync_booking_to_google` is NOT scheduled
