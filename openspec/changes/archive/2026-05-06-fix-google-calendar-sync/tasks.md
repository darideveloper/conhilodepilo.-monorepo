# Tasks: fix-google-calendar-sync

## 1. Service layer (`dashboard/utils/google_calendar.py`)
- [x] 1.1 Add `_call_with_retry(callable_factory, *, attempts=3, backoff=(1,2,4))` helper that retries on `HttpError` with status >= 500, `socket.error`, `ssl.SSLError`, and `httplib2.HttpLib2Error`; non-transient errors propagate immediately.
- [x] 1.2 Keep `settings.TIME_ZONE` as the event timezone in `booking_to_event_body`. No company-level override (CompanyProfile does not store a timezone).
- [x] 1.3 Add `extendedProperties.private = {"booking_id": str(booking.pk)}` and `iCalUID = f"booking-{pk}@{HOST_DOMAIN}"` to event body. (`iCalUID` is informational; dedupe is via the extendedProperty lookup in 1.3a.)
- [x] 1.3a Implement lookup-before-insert in `sync_booking_to_google`: if `booking.google_event_id` is unset, call `events().list(privateExtendedProperty=f"booking_id={booking.pk}", showDeleted=False, maxResults=1)` first; if a result is returned, set `booking.google_event_id` and switch to `patch`. Only call `insert` when no result is returned.
- [x] 1.4 When booking status is `CANCELLED`, prefix the `summary` with `"[CANCELLED] "` (idempotent — don't double-prefix).
- [x] 1.5 Add `client_email` to description.
- [x] 1.6 Replace `str(e)[:1000]` with structured formatter: for `HttpError`, store `"{status} {reason}: {detail}"`; for other exceptions, store class name + message (truncated to 1000 chars).
- [x] 1.7 In `delete_google_calendar_event`, treat HTTP 404 and 410 as success (no log error). All other errors logged + recorded.
- [x] 1.8 Wire `_call_with_retry` around every `events().insert/patch/delete().execute()` call.

## 2. Model changes (`dashboard/booking/models.py`)
- [x] 2.1 Add `Booking.updated_at = DateTimeField(auto_now=True, null=True)`.
- [x] 2.2 Remove the in-file `m2m_changed` receiver `update_booking_end_time` from `models.py` (moved to `signals.py` in section 3).
- [x] 2.3 Generate Django migration for new fields. Run `cd dashboard && python manage.py makemigrations booking`.

## 3. Signal restructure (`dashboard/booking/signals.py`)
- [x] 3.1 Track previous `status` per `Booking` instance (override `__init__` on the model OR snapshot in `pre_save`) so signal handlers can detect transitions.
- [x] 3.2 Move `m2m_changed` receiver from `models.py` here. After recalculating `end_time` and saving, schedule `sync_booking_to_google(instance)` via `transaction.on_commit` when `instance.status != "PENDING"` and at least one service is attached.
- [x] 3.3 In `post_save`:
  - Keep skip when `update_fields` ⊆ `{google_event_id, google_sync_status, google_sync_error, last_synced_at, end_time}`. (`end_time` is in the skip-set because the m2m_changed handler and `Booking.save()`'s recomputation both save with `update_fields` containing `end_time`; m2m_changed is the sole sync trigger for service/time changes.)
  - Remove the `created=True` early-return.
  - When status transitioned `* → CANCELLED` and `google_event_id` set, schedule a sync (will patch with `[CANCELLED]` prefix from 1.4).
  - When status is `PENDING`, do nothing (pre-paid path waits for Stripe webhook).
  - Otherwise, schedule `sync_booking_to_google` via `transaction.on_commit`.
- [x] 3.4 `post_delete` handler: keep, but now uses improved delete error handling from 1.7.

## 4. View changes (`dashboard/booking/views.py`)
- [x] 4.1 In `CreateBookingView.post`, after `booking.services.set(services)` and before returning, add `transaction.on_commit(lambda: sync_booking_to_google(booking))` when `status == "CONFIRMED"`.
- [x] 4.2 In `StripeWebhookView`, no functional change required; verify the existing `booking.save(update_fields=['status', 'stripe_payment_id'])` still triggers `post_save` → sync.
- [x] 4.3 Wrap the booking creation block in `transaction.atomic()` so `transaction.on_commit` is well-defined.

## 5. Admin (`dashboard/booking/admin.py`)
- [x] 5.1 Update existing `retry_google_calendar_sync` to use the new sync flow.
- [x] 5.2 Add new admin action `reconcile_selected_bookings_with_google` that runs reconciliation logic on the selected queryset.
- [x] 5.3 Add Spanish translations in `locale/es/LC_MESSAGES/django.po` for the new action label.

## 6. Reconciliation command (new)
- [x] 6.1 Create `dashboard/booking/management/commands/reconcile_google_calendar.py`.
- [x] 6.2 Add `--dry-run` flag.
- [x] 6.3 Pass 1: `Booking.objects.filter(google_sync_status="FAILURE")` → call `sync_booking_to_google`.
- [x] 6.4 Pass 2: `Booking.objects.filter(google_sync_status="SUCCESS", last_synced_at__lt=F("updated_at"))` → call `sync_booking_to_google`.
- [x] 6.5 Pass 3: page through `events().list(calendarId=GOOGLE_CALENDAR_ID, showDeleted=False, pageToken=...)` (full unfiltered list — Google API does not support wildcards on `privateExtendedProperty`). Client-side, filter to events whose `extendedProperties.private.booking_id` exists and does not match any `Booking.pk`. Report only — never auto-delete.
- [x] 6.6 Print a summary: `<n> failures retried, <m> drift fixed, <k> orphans reported`.

## 7. Tests (`dashboard/booking/tests_integrations.py`)
- [x] 7.1 Set up a fixture that mocks `googleapiclient.discovery.build` and captures every call to `insert/patch/delete` (event body + kwargs).
- [x] 7.2 Test: CONFIRMED booking creation → exactly one `insert` call after commit.
- [x] 7.3 Test: PENDING (pre-paid) booking creation → zero calendar API calls.
- [x] 7.4 Test: Stripe webhook flips PENDING → PAID → exactly one `insert` call.
- [x] 7.5 Test: m2m service swap with same total duration → exactly one `patch` call; description reflects new service names.
- [x] 7.6 Test: `start_time` change → `patch` call with new `dateTime` values.
- [x] 7.7 Test: status → CANCELLED → `patch` call; summary starts with `[CANCELLED] `; event NOT deleted; `google_event_id` retained.
- [x] 7.8 Test: `Booking.delete()` → `events().delete()` call; 404/410 treated as success (parameterized).
- [x] 7.9 Test: Patch fails with HTTP 404 → fallback `insert` is called and new `google_event_id` saved.
- [x] 7.10 Test: Lookup-before-insert recovery — booking has `google_event_id=None` but `events().list` returns one event with matching `booking_id` → code calls `patch` with the discovered id (not `insert`) and persists the id back to the booking.
- [x] 7.11 Test: every `insert/patch/delete` call carries `sendUpdates="none"` and event body has NO `attendees` key.
- [x] 7.12 Test: event body contains `extendedProperties.private.booking_id == str(booking.pk)`.
- [x] 7.13 Test: event `start.timeZone` and `end.timeZone` equal `settings.TIME_ZONE` (use `override_settings(TIME_ZONE="America/Mexico_City")` to verify the value is read dynamically).
- [x] 7.14 Test: HTTP 503 from insert → retried 3 times then marked FAILURE; `google_sync_error` includes `503`.
- [x] 7.15 Test: `transaction.on_commit` deferral — sync is NOT called inside the atomic block; called after commit.
- [x] 7.16 Test: `reconcile_google_calendar` command picks up FAILURE bookings and retries them.
- [x] 7.17 Test: reconcile command picks up SUCCESS bookings where `last_synced_at < updated_at` and re-syncs.

## 8. Validation
- [x] 8.1 Run `cd dashboard && python manage.py test booking -v 2` — all pass.
- [x] 8.2 Run `openspec validate fix-google-calendar-sync --strict` — no errors.
- [x] 8.3 Manual smoke (staging service account):
  - Create CONFIRMED booking via API → event appears.
  - Edit services in admin → description updates.
  - Edit `start_time` in admin → event time updates.
  - Set status CANCELLED → summary prefixed.
  - Hard delete → event removed.
  - Create PRE-PAID booking → no event → complete Stripe checkout → event appears.
  - Run `python manage.py reconcile_google_calendar --dry-run` → reports 0 drift.

## 9. Follow-ups (out of scope)
- [ ] 9.1 Schedule `reconcile_google_calendar` via cron (django-crontab or systemd timer).
- [ ] 9.2 Optional: surface orphan events in admin dashboard.
