# Change: Fix Google Calendar booking sync gaps

## Why
Audit of the current Google Calendar integration revealed multiple bugs that break the goal of 100% booking ↔ calendar sync: bookings created with services attached only sync as a side-effect of `end_time` recalculation; cancelling a booking leaves the event on the calendar with `Estado: Cancelled` instead of marking it visibly; pre-paid bookings depend entirely on the Stripe webhook firing successfully (no fallback); a successful `events().insert()` followed by a DB write failure produces duplicate events; the integration uses `settings.TIME_ZONE` instead of the company timezone; `httpError` details are stringified with `str(e)`; and there is no reconciliation path for drift.

## What Changes
- **A. Sync triggers** — Make sync explicit (no longer dependent on `end_time` save side-effect):
  - `CreateBookingView` defers an explicit `sync_booking_to_google` call via `transaction.on_commit` after `services.set(...)` (only when status is CONFIRMED).
  - `m2m_changed` receiver (moved from `models.py` to `booking/signals.py`) calls sync directly when status is non-PENDING.
  - `post_save` keeps the `update_fields` skip-set for internal Google fields; "skip on created" is removed.
- **B. Cancelled bookings** — Status transition to `CANCELLED` patches the event with a `[CANCELLED]` prefix on the summary; the event stays on the calendar as a record. Hard delete still removes the event.
- **C. Reliability** — Wrap calendar API calls in a retry helper (3 attempts, 1s/2s/4s backoff) for transient errors (5xx, socket, SSL). Defer all sync from the request hot path via `transaction.on_commit`.
- **D. Idempotency** — Tag every event with `extendedProperties.private.booking_id = <pk>`. Before calling `events().insert`, look up the existing event for the booking with `events().list(privateExtendedProperty=f"booking_id={booking.pk}")`; if found, switch to `events().patch` against the returned event id. (`iCalUID` alone does NOT dedupe `events.insert` in the Google API — only `events.import` performs iCalUID dedupe. We use the `extendedProperties` lookup instead.) Also include `iCalUID = booking-<pk>@<HOST_DOMAIN>` for human/audit traceability.
- **E. Notifications** — Keep `sendUpdates="none"` and do NOT add `attendees`. Calendar is internal-only.
- **F. Timezone** — Continue using `settings.TIME_ZONE` (the project standard, `Europe/Madrid` in production). No `CompanyProfile.timezone` field is added — `CompanyProfile` does not store a timezone.
- **G. Error recording** — Capture `HttpError` status code + reason in `google_sync_error` (structured), not `str(e)`.
- **H. Delete idempotency** — Treat 404 and 410 from `events().delete()` as success.
- **I. Reconciliation** — Add `manage.py reconcile_google_calendar [--dry-run]` to retry FAILURE bookings, re-sync drift (using a new `Booking.updated_at` field), and report orphan events. Cron scheduling is a follow-up.
- **J. Tests** — Replace and extend `tests_integrations.py` to cover all the above scenarios.

## Impact
- **Affected specs:**
  - `booking-google-sync` (MODIFIED + ADDED requirements)
  - `google-calendar-service` (MODIFIED + ADDED requirements)
- **Affected code:**
  - `dashboard/utils/google_calendar.py` — event body builder, retry helper, error recording, delete idempotency
  - `dashboard/booking/signals.py` — restructured; m2m_changed handler moved here
  - `dashboard/booking/models.py` — add `updated_at` field; remove m2m_changed handler
  - `dashboard/booking/views.py` — explicit `transaction.on_commit` sync in `CreateBookingView`
  - `dashboard/booking/admin.py` — reconcile admin action
  - `dashboard/booking/tests_integrations.py` — extended coverage
  - `dashboard/booking/management/commands/reconcile_google_calendar.py` — new
- **DB migration:** Add `Booking.updated_at` (auto_now=True).
- **No new dependencies.** Stays within Django; no Celery/Redis.
