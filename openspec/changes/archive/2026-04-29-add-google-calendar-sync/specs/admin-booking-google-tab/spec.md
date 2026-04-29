## ADDED Requirements

### Requirement: Dedicated Google Calendar Tab in BookingAdmin
The `BookingAdmin` detail page MUST display a dedicated **"Google Calendar"** tab containing all four Google sync fields: `google_event_id`, `google_sync_status`, `google_sync_error`, and `last_synced_at`. All four fields MUST be read-only. This replaces the current collapsed "Integrations" fieldset where `google_event_id` is currently shown.

#### Scenario: Admin opens booking detail
- **WHEN** an admin navigates to a `Booking` detail page
- **THEN** a "Google Calendar" tab is visible alongside the existing tabs
- **AND** the tab shows `google_event_id`, `google_sync_status`, `google_sync_error`, and `last_synced_at`
- **AND** all four fields are read-only

#### Scenario: Failed sync is visible
- **WHEN** a booking has `google_sync_status = "FAILURE"`
- **THEN** the error message in `google_sync_error` is visible in the Google Calendar tab

### Requirement: Google Sync Status in Booking List
The `BookingAdmin` list view MUST display a computed `google_sync_status_badge` column with color-coded indicators: green for SUCCESS, red for FAILURE, yellow for PENDING, grey for DISABLED.

#### Scenario: List view shows sync health
- **WHEN** an admin views the booking list
- **THEN** each row shows a colored badge indicating the Google Calendar sync status
- **AND** FAILURE rows are immediately distinguishable (red)

### Requirement: Manual Retry Admin Action
The `BookingAdmin` MUST include an admin action **"Retry Google Calendar Sync"** available on the booking list view. When applied to selected bookings, it calls `sync_booking_to_google` for each and updates their sync fields.

#### Scenario: Admin retries sync after credential update
- **GIVEN** several bookings with `google_sync_status = "FAILURE"` due to a past credential issue
- **WHEN** the admin selects them and applies "Retry Google Calendar Sync"
- **THEN** each booking is re-synced and their status updated to `"SUCCESS"` or `"FAILURE"` accordingly
- **AND** a success message reports how many were synced

### Requirement: Stripe Payment Tab Separation
`stripe_payment_id` MUST remain in the existing "Integrations" fieldset (or its own tab) and MUST NOT be moved to the Google Calendar tab.

#### Scenario: Stripe field remains accessible
- **WHEN** an admin opens a booking detail
- **THEN** `stripe_payment_id` is visible under the "Integrations" section, separate from Google Calendar fields
