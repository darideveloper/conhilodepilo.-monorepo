# Design: add-google-calendar-sync

## Context
The project is a single-company Django admin dashboard (`backend/booking/`). There are no tenants; `CompanyProfile` is a `SingletonModel`. The `Booking` model already stores `google_event_id` (CharField). Settings already reads `GOOGLE_CALENDAR_ID` from env. No Google API libraries are installed yet and no service layer exists.

## Architecture

### Authentication
A Google Service Account (server-to-server OAuth2) is used. The JSON credentials are stored in `GOOGLE_SERVICE_ACCOUNT_JSON` as either a raw JSON string or a file path. At startup, `get_google_calendar_service()` in `backend/utils/google_calendar.py` parses the credential and builds an authorized `googleapiclient.discovery` service object scoped to `https://www.googleapis.com/auth/calendar`.

### Event Mapping
`booking_to_event_body(booking)` converts a `Booking` instance into a Google Calendar event dict:
- `summary`: `"{client_name} — {service_names}"`
- `start` / `end`: ISO 8601 datetimes from `booking.start_time` / `booking.end_time`
- `description`: service names, price, client phone, special requests
- `sendUpdates`: always `"none"` — suppresses all Google-originated email notifications

### Sync Lifecycle
```
Booking.post_save  ──► sync_booking_to_google(booking)
                         ├── has google_event_id?
                         │   ├── yes → events().patch()  (404 → re-insert)
                         │   └── no  → events().insert()
                         └── update google_event_id, google_sync_status, last_synced_at

Booking.post_delete ──► delete_google_calendar_event(booking)
                          └── events().delete() if google_event_id present
```

Signals are defined in `backend/booking/signals.py` and wired up in `BookingConfig.ready()` inside `backend/booking/apps.py`.

### Notification Suppression
`sendUpdates='none'` is hardcoded on every `insert`, `patch`, and `delete` API call. This is the only mechanism needed — no additional configuration.

### Error Handling
All API calls are wrapped in try/except. On failure:
- `google_sync_status` → `"FAILURE"`
- `google_sync_error` → exception message (truncated to 1000 chars)
- `last_synced_at` unchanged
- Exception is logged via `logging.getLogger(__name__)` but not re-raised (booking saves must not fail due to calendar errors)

On success:
- `google_sync_status` → `"SUCCESS"`
- `google_sync_error` → `""`
- `last_synced_at` → `now()`

### Guard: GOOGLE_CALENDAR_ID not configured
If `settings.GOOGLE_CALENDAR_ID` or `settings.GOOGLE_SERVICE_ACCOUNT_JSON` is empty/None, `sync_booking_to_google` sets `google_sync_status = "DISABLED"` and returns immediately without making any API call.

### Admin Tab
`BookingAdmin` is updated:
- Remove `google_event_id` from the existing `"Integrations"` collapsed fieldset
- Add a new `"Google Calendar"` fieldset containing `google_event_id`, `google_sync_status`, `google_sync_error`, `last_synced_at`
- Wire the new fieldset into a new `"Google Calendar"` tab (using Unfold's `tabs` list)
- All four fields are `readonly_fields`
- Add `google_sync_status_badge` computed column to `list_display` with color coding
- Add `"retry_google_calendar_sync"` admin action

## Trade-offs

| Decision | Rationale |
|---|---|
| Sync is synchronous (in-band with save) | Simplest path; no Celery/queue required. Calendar API calls are fast (<500ms). Admin saves are infrequent. |
| Credentials as env var string (not file path) | Consistent with project convention (all secrets are env vars). String is JSON-decoded at runtime. |
| `post_save` fires on every save | Ensures calendar always reflects latest state without a separate update mechanism. Guards against double-sync via `update_fields` check are intentionally omitted to keep the logic simple. |
| Signals in separate `signals.py` | Keeps `models.py` clean; `apps.py.ready()` is the established Django pattern. |
