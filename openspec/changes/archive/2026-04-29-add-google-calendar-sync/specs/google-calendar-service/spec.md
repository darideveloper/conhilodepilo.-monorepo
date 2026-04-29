## ADDED Requirements

### Requirement: Google Calendar Service Layer
The system MUST provide a `backend/utils/google_calendar.py` module that authenticates with the Google Calendar API using a Service Account and exposes three public functions: `sync_booking_to_google`, `delete_google_calendar_event`, and `get_google_calendar_service`.

#### Scenario: Successful event creation
- **GIVEN** `GOOGLE_CALENDAR_ID` and `GOOGLE_SERVICE_ACCOUNT_JSON` are set in settings
- **AND** a `Booking` with no `google_event_id` is passed to `sync_booking_to_google`
- **WHEN** the function executes
- **THEN** a new event is inserted into the configured calendar
- **AND** the function returns the new `google_event_id` string

#### Scenario: Successful event update (patch)
- **GIVEN** a `Booking` that already has a `google_event_id`
- **WHEN** `sync_booking_to_google` is called
- **THEN** the existing calendar event is patched with the latest booking data
- **AND** `sendUpdates` is set to `"none"` on the API call

#### Scenario: Self-healing on 404
- **GIVEN** a `Booking` with a stale `google_event_id` that no longer exists in Google Calendar
- **WHEN** `sync_booking_to_google` is called and the patch returns HTTP 404
- **THEN** the system automatically falls back to `events().insert()`
- **AND** the new `google_event_id` is returned

#### Scenario: Event deletion
- **GIVEN** a `Booking` with a `google_event_id`
- **WHEN** `delete_google_calendar_event` is called
- **THEN** the calendar event is deleted using `events().delete()` with `sendUpdates='none'`

#### Scenario: No-op when credentials not configured
- **GIVEN** `GOOGLE_CALENDAR_ID` or `GOOGLE_SERVICE_ACCOUNT_JSON` is blank/None in settings
- **WHEN** `sync_booking_to_google` is called
- **THEN** no API call is made
- **AND** the function returns `"DISABLED"` as the status

### Requirement: Notification Suppression
Every Google Calendar API call (insert, patch, delete) MUST include `sendUpdates='none'` to prevent Google from sending any email notifications from the business owner's Google account.

#### Scenario: Insert with notifications suppressed
- **WHEN** a new calendar event is created
- **THEN** the API request body or query param includes `sendUpdates='none'`
- **AND** no email notification is dispatched by Google

### Requirement: Google API Dependencies
The `backend/requirements.txt` MUST include `google-api-python-client`, `google-auth-httplib2`, and `google-auth-oauthlib`.

#### Scenario: Fresh install
- **WHEN** `pip install -r requirements.txt` is run
- **THEN** the `googleapiclient` and `google.oauth2` packages are available for import

### Requirement: Service Account Environment Variable
Settings MUST read `GOOGLE_SERVICE_ACCOUNT_JSON` from the environment. The value is the raw JSON string of the service account credentials (or `None`/empty to disable).

#### Scenario: Settings loads credential from env
- **GIVEN** `GOOGLE_SERVICE_ACCOUNT_JSON='{...}'` is set in `.env`
- **WHEN** Django starts
- **THEN** `settings.GOOGLE_SERVICE_ACCOUNT_JSON` holds the string value
