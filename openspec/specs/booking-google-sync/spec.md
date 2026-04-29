# booking-google-sync Specification

## Purpose
TBD - created by archiving change add-google-calendar-sync. Update Purpose after archive.
## Requirements
### Requirement: Booking Google Sync State Fields
The `Booking` model MUST store three additional fields to track synchronization state with Google Calendar:
- `google_sync_status`: CharField with choices `PENDING | SUCCESS | FAILURE | DISABLED`, default `PENDING`
- `google_sync_error`: TextField (null, blank) — stores error message on failure, cleared on success
- `last_synced_at`: DateTimeField (null, blank) — updated on each successful sync

These complement the existing `google_event_id` field already present on the model.

#### Scenario: Initial booking has PENDING status
- **WHEN** a new `Booking` is created in the admin
- **THEN** `google_sync_status` defaults to `"PENDING"` before the signal fires

#### Scenario: Status after successful sync
- **WHEN** `sync_booking_to_google` completes without error
- **THEN** `google_sync_status` is set to `"SUCCESS"`
- **AND** `google_sync_error` is cleared
- **AND** `last_synced_at` is updated to the current UTC time

#### Scenario: Status after failed sync
- **WHEN** the Google Calendar API returns an error
- **THEN** `google_sync_status` is set to `"FAILURE"`
- **AND** `google_sync_error` holds the error detail
- **AND** the booking save is NOT rolled back (calendar errors must not block booking creation)

### Requirement: Automatic Sync via Django Signals
A `post_save` signal on `Booking` MUST automatically call `sync_booking_to_google` after every create or update. A `post_delete` signal MUST call `delete_google_calendar_event` when a booking is removed. Signals MUST be registered in `backend/booking/signals.py` and connected in `BookingConfig.ready()`.

#### Scenario: Booking created from admin
- **WHEN** a new booking is saved via the Django admin
- **THEN** `post_save` fires and `sync_booking_to_google` is called automatically

#### Scenario: Booking status updated from admin
- **WHEN** an admin changes a booking's status (e.g., PENDING → CONFIRMED) and saves
- **THEN** the corresponding Google Calendar event is patched with updated data

#### Scenario: Booking deleted from admin
- **WHEN** a booking is deleted from the Django admin
- **THEN** `post_delete` fires and the corresponding Google Calendar event is removed

