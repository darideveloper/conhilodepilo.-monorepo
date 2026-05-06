## MODIFIED Requirements

### Requirement: Notification Suppression
Every Google Calendar API call (insert, patch, delete) MUST include `sendUpdates="none"` to prevent Google from sending any email notifications from the business owner's Google account. The event body MUST NOT include an `attendees` field — the calendar is internal-only and clients are not invited via Google Calendar.

#### Scenario: Insert with notifications suppressed
- **WHEN** a new calendar event is created
- **THEN** the API request body or query param includes `sendUpdates="none"`
- **AND** the event body has no `attendees` key
- **AND** no email notification is dispatched by Google

#### Scenario: Patch with notifications suppressed
- **WHEN** an existing event is patched
- **THEN** `sendUpdates="none"` is set
- **AND** no `attendees` key is sent

#### Scenario: Delete with notifications suppressed
- **WHEN** `events().delete` is called
- **THEN** `sendUpdates="none"` is set

## ADDED Requirements

### Requirement: Idempotent Event Creation
Every event body produced by `booking_to_event_body` MUST include:
- An `extendedProperties.private.booking_id = str(booking.pk)` for lookup-based deduplication.
- An `iCalUID` of the form `booking-<booking.pk>@<HOST_DOMAIN>`, where `<HOST_DOMAIN>` is derived from `settings.HOST` (or `localhost` if unset). The `iCalUID` is informational/audit-only — it is NOT relied upon for dedupe because `events.insert` ignores duplicate iCalUIDs.

Before calling `events().insert`, `sync_booking_to_google` MUST attempt to recover an existing event for the booking by calling:

```
events().list(
    calendarId=GOOGLE_CALENDAR_ID,
    privateExtendedProperty=f"booking_id={booking.pk}",
    showDeleted=False,
    maxResults=1,
).execute()
```

If a result is returned, the function MUST switch to `events().patch(eventId=<found.id>)` and persist `<found.id>` to `booking.google_event_id`. Only if zero results are returned does it call `events().insert`. This protects against the case where a prior `insert` succeeded but the subsequent DB write of `google_event_id` failed.

#### Scenario: Body includes booking_id and iCalUID
- **WHEN** `booking_to_event_body(booking)` is called for booking with pk=42
- **THEN** the returned dict contains `extendedProperties.private.booking_id == "42"`
- **AND** `iCalUID == "booking-42@<HOST_DOMAIN>"`

#### Scenario: Recovery from prior insert+DB-write failure
- **GIVEN** a prior `events().insert` succeeded but the DB write of `google_event_id` failed (booking has `google_event_id=None` but a calendar event exists with `extendedProperties.private.booking_id=str(booking.pk)`)
- **WHEN** `sync_booking_to_google(booking)` runs again
- **THEN** `events().list(privateExtendedProperty="booking_id=<pk>")` is called first
- **AND** the function calls `events().patch` against the discovered event id (not `insert`)
- **AND** `booking.google_event_id` is updated to the discovered id
- **AND** no duplicate calendar event is created

#### Scenario: Fresh booking with no prior event
- **GIVEN** a booking with `google_event_id=None` and no matching extendedProperty event in the calendar
- **WHEN** `sync_booking_to_google(booking)` runs
- **THEN** `events().list` returns zero results
- **AND** `events().insert` is called once

### Requirement: Settings Timezone
Event `start.timeZone` and `end.timeZone` MUST resolve to `settings.TIME_ZONE` at call time (not cached at module import). `CompanyProfile` does not store a timezone; the timezone is sourced exclusively from Django's `TIME_ZONE` setting (which is read from the `TIME_ZONE` env var with a project default). The datetimes themselves MUST remain ISO-formatted aware datetimes converted with `timezone.localtime`.

#### Scenario: Event uses settings.TIME_ZONE
- **GIVEN** `settings.TIME_ZONE` is configured (any IANA tz)
- **WHEN** `booking_to_event_body(booking)` is called
- **THEN** `start.timeZone == settings.TIME_ZONE`
- **AND** `end.timeZone == settings.TIME_ZONE`

#### Scenario: Timezone is resolved at call time, not import time
- **GIVEN** a test uses `override_settings(TIME_ZONE="America/Mexico_City")`
- **WHEN** `booking_to_event_body(booking)` is called inside the override context
- **THEN** `start.timeZone == "America/Mexico_City"`

### Requirement: Retry With Backoff on Transient Errors
`sync_booking_to_google` and `delete_google_calendar_event` MUST wrap each Google API `.execute()` call in a retry helper that retries up to 3 attempts with exponential backoff (1s, 2s, 4s) on the following transient errors:
- `googleapiclient.errors.HttpError` with `resp.status >= 500`
- `socket.error`
- `ssl.SSLError`
- `httplib2.HttpLib2Error`

Non-transient errors (e.g., HTTP 4xx other than the 404 fallback for patch) MUST propagate immediately without retry. After all attempts fail, the booking's `google_sync_status` MUST be set to `"FAILURE"` and `google_sync_error` populated.

#### Scenario: Transient 503 retried
- **WHEN** `events().insert().execute()` raises `HttpError` with status 503 twice, then succeeds
- **THEN** the call is retried twice with backoff
- **AND** the booking ends with `google_sync_status="SUCCESS"`

#### Scenario: All retries exhausted
- **WHEN** `events().insert().execute()` raises `HttpError` with status 503 on all 3 attempts
- **THEN** `google_sync_status="FAILURE"`
- **AND** `google_sync_error` contains `"503"`

#### Scenario: Non-transient 4xx fails fast
- **WHEN** `events().insert().execute()` raises `HttpError` with status 400
- **THEN** no retry is attempted
- **AND** `google_sync_status="FAILURE"` immediately

### Requirement: Structured Error Recording
On failure, `google_sync_error` MUST contain a structured message:
- For `googleapiclient.errors.HttpError`: `f"{status} {reason}: {detail}"` truncated to 1000 chars.
- For other exceptions: `f"{type(e).__name__}: {e}"` truncated to 1000 chars.

#### Scenario: HttpError formatted with status code
- **WHEN** an `HttpError` with status 403 reason "Forbidden" is raised
- **THEN** `google_sync_error` starts with `"403 Forbidden: "`

### Requirement: Delete Idempotency
`delete_google_calendar_event` MUST treat HTTP 404 (Not Found) and HTTP 410 (Gone) responses as success — the event is already absent from the calendar, which is the intended terminal state. Other errors MUST be logged and recorded.

#### Scenario: Delete on already-removed event
- **GIVEN** the calendar event was already deleted manually
- **WHEN** `delete_google_calendar_event` is called and the API returns 404 or 410
- **THEN** no error is logged at ERROR level
- **AND** the function returns silently

#### Scenario: Delete fails with non-idempotent error
- **WHEN** `delete_google_calendar_event` receives an HTTP 500
- **THEN** the retry helper retries 3 times
- **AND** if still failing, the error is logged

### Requirement: Reconciliation Management Command
The system MUST provide a Django management command `python manage.py reconcile_google_calendar [--dry-run]` that performs three passes:

1. **Failure retry**: For every booking with `google_sync_status="FAILURE"`, call `sync_booking_to_google`.
2. **Drift detection**: For every booking with `google_sync_status="SUCCESS"` and `last_synced_at < updated_at`, call `sync_booking_to_google`.
3. **Orphan reporting**: Page through `events().list(calendarId=GOOGLE_CALENDAR_ID, showDeleted=False)` (Google API does NOT support wildcards on `privateExtendedProperty`, so the listing is unfiltered and pagination must be honored via `pageToken`). Filter client-side to events whose `extendedProperties.private.booking_id` exists and does not match any current `Booking.pk`. Report only — do not auto-delete.

The command MUST print a summary line: `<n> failures retried, <m> drift fixed, <k> orphans reported`. The `--dry-run` flag MUST suppress all writes (both DB and Google API mutations) and only report what would happen.

#### Scenario: Failure retry succeeds
- **GIVEN** a booking with `google_sync_status="FAILURE"`
- **WHEN** `manage.py reconcile_google_calendar` runs
- **THEN** `sync_booking_to_google` is called for that booking
- **AND** if successful, the booking's status becomes `"SUCCESS"`

#### Scenario: Drift re-syncs
- **GIVEN** a booking where `last_synced_at < updated_at` (admin edited fields after last sync)
- **WHEN** the command runs
- **THEN** the booking is re-synced

#### Scenario: Dry-run makes no changes
- **GIVEN** several FAILURE bookings
- **WHEN** `manage.py reconcile_google_calendar --dry-run` runs
- **THEN** no API calls are made
- **AND** no DB writes occur
- **AND** the summary still reports counts as if the run had executed

#### Scenario: Orphan event reported
- **GIVEN** a calendar event with `extendedProperties.private.booking_id="9999"` and no Booking with pk=9999
- **WHEN** the command runs
- **THEN** the orphan is included in the orphan report
- **AND** the orphan is NOT deleted
