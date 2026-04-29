## Tasks: add-google-calendar-sync

### 1. Dependencies & Configuration
- [x] 1.1 Add `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` to `backend/requirements.txt`
- [x] 1.2 Add `GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")` to `backend/project/settings.py` (next to the existing `GOOGLE_CALENDAR_ID` line)

### 2. Service Layer
- [x] 2.1 Create `backend/utils/google_calendar.py` with:
  - `get_google_calendar_service()` — parses `GOOGLE_SERVICE_ACCOUNT_JSON` (JSON string), builds and returns an authorized `googleapiclient` service object; returns `None` if credentials not configured
  - `booking_to_event_body(booking)` — maps `Booking` fields to a Google Calendar event dict; always includes `sendUpdates='none'` behavior (set at call-site, not in body)
  - `sync_booking_to_google(booking)` — insert or patch; handles 404 self-healing; updates `google_sync_status`, `google_sync_error`, `last_synced_at` on the booking; returns early with `DISABLED` if credentials missing
  - `delete_google_calendar_event(booking)` — deletes event if `google_event_id` present; no-ops silently if missing

### 3. Model Migration
- [x] 3.1 Add three fields to `Booking` in `backend/booking/models.py`:
  - `google_sync_status` (CharField, choices, default `"PENDING"`)
  - `google_sync_error` (TextField, null, blank)
  - `last_synced_at` (DateTimeField, null, blank)
- [x] 3.2 Generate and apply migration: `python manage.py makemigrations booking && python manage.py migrate`

### 4. Signals
- [x] 4.1 Create `backend/booking/signals.py` with `post_save` and `post_delete` receivers on `Booking`
  - `post_save`: call `sync_booking_to_google(instance)` — guard against infinite recursion by using `update_fields` on the nested save inside the service
  - `post_delete`: call `delete_google_calendar_event(instance)`
- [x] 4.2 Connect signals in `BookingConfig.ready()` inside `backend/booking/apps.py`

### 5. Admin Dashboard
- [x] 5.1 Add `google_sync_status`, `google_sync_error`, `last_synced_at` to `readonly_fields` in `BookingAdmin`
- [x] 5.2 Add a new `"Google Calendar"` fieldset to `BookingAdmin.fieldsets` containing `google_event_id`, `google_sync_status`, `google_sync_error`, `last_synced_at`
- [x] 5.3 Remove `google_event_id` from the existing `"Integrations"` fieldset
- [x] 5.4 Add `"Google Calendar"` tab entry to `BookingAdmin.tabs`
- [x] 5.5 Add `google_sync_status_badge` computed method to `BookingAdmin` that returns HTML with color-coded badge; add to `list_display`
- [x] 5.6 Add `retry_google_calendar_sync` admin action method; register it in `BookingAdmin.actions`

### 6. Validation
- [x] 6.1 Run `openspec validate add-google-calendar-sync --strict` and resolve any issues
- [x] 6.2 Manual smoke test: create a booking in admin → verify event appears in Google Calendar
- [x] 6.3 Manual smoke test: update booking status → verify calendar event is patched
- [x] 6.4 Manual smoke test: delete booking → verify calendar event is removed
- [x] 6.5 Manual smoke test: set blank credentials → verify sync status becomes DISABLED and no exception is raised

### 7. Stability & Correctness Fixes
- [x] 7.1 Prevent empty syncs: Skip synchronization during initial `post_save` (creation) to wait for services to be attached.
- [x] 7.2 Duplication prevention: Update the `Booking` instance attributes in memory during sync to prevent race conditions.
- [x] 7.3 Automatic End Time Recalculation: Override `Booking.save()` to ensure `end_time` is updated whenever `start_time` changes.

### 8. Localization & UI Refinement
- [x] 8.1 Spanish translations: Add translations for sync actions, status badges, and success messages in `django.po`.
- [x] 8.2 Fix translation logic: Refactor f-strings in `admin.py` to use proper `.format()` for gettext compatibility.

### 9. Automated Testing
- [x] 9.1 Sync logic verification: Create `tests_google_calendar.py` to verify multi-step sync flow.
- [x] 9.2 End time verification: Create `tests_end_time.py` to ensure scheduling consistency.

### Dependencies / Order
Tasks 1 → 2 → 3 → 4 → 5 must be done sequentially. Tasks 7, 8, and 9 were added to resolve implementation-phase bugs and provide robust localization. Task 6 and 9 are for final verification.
