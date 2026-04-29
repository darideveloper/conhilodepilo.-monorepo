# booking-ui Specification

## Purpose
TBD - created by archiving change fix-timezone-mismatch. Update Purpose after archive.
## Requirements
### Requirement: Timezone Consistency
The system MUST use `Europe/Madrid` as the primary timezone for business logic and data display.

#### Scenario: Backend Timezone Configuration
- GIVEN the backend application environment variables
- THEN the `TIME_ZONE` MUST be configured as `Europe/Madrid`.

### Requirement: Accurate Availability Display
The booking calendar MUST display available days exactly as returned by the API, without 1-day shifts due to client-side timezone offsets.

#### Scenario: Parsing Availability Dates
- GIVEN a list of available date strings in "YYYY-MM-DD" format from the API
- WHEN the frontend parses these strings into `Date` objects
- THEN it MUST parse them as local dates (e.g., using `new Date(year, month, day)`) to avoid UTC-to-local shifts.

### Requirement: Persistent Date Integrity
The application MUST maintain the correct selected date after page refreshes, regardless of the user's timezone offset.

#### Scenario: Rehydrating Selected Date
- GIVEN a stored selected date
- WHEN the application rehydrates its state from local storage
- THEN the revived `Date` object MUST represent the same calendar day as originally selected.

### Requirement: Time Slot Selection
The system MUST allow users to select an available time slot after choosing a valid day.

#### Scenario: Displaying available times
- **WHEN** a valid day is selected in the booking calendar
- **THEN** the UI MUST present a list of available time slots and require the user to pick one before proceeding to the contact form.

### Requirement: Minimal Contact Information
The system MUST collect only necessary contact information without arbitrary extra fields.

#### Scenario: Completing the contact form
- **WHEN** the user proceeds to the contact info step
- **THEN** they MUST be prompted for Name, Email, and Special Requests, and MUST NOT be prompted for Number of Guests.

### Requirement: Dynamic Privacy Policy Link
The system MUST link to the dynamically configured privacy policy URL in the booking form.

#### Scenario: Accepting privacy policy
- **WHEN** the privacy policy checkbox is displayed
- **THEN** the accompanying text MUST link to the URL provided by the backend configuration.

### Requirement: Full Confirmation Summary
The system MUST display a final confirmation summary after a successful booking.

#### Scenario: Showing success screen
- **WHEN** the booking is successfully submitted to the API
- **THEN** the success screen MUST display the collected client Name, Email, Date, Time Slot, and selected Services.

### Requirement: Error Feedback
The system MUST gracefully handle and display API errors during submission.

#### Scenario: Booking submission failure
- **WHEN** the booking submission fails (e.g., slot no longer available)
- **THEN** the UI MUST display a clear error message and allow the user to correct their input without crashing.

### Requirement: Split persistence between Local and Session storage
The application MUST distinguish between persistent user data and ephemeral booking data.

#### Scenario: User Identity Persistence
- **GIVEN** a user has entered their name, email, and phone in the booking form
- **WHEN** the user closes the browser and returns later
- **THEN** the name, email, and phone fields MUST be pre-filled from `localStorage`.

#### Scenario: Booking Session Isolation
- **GIVEN** a user has selected a service, date, and time in one tab
- **WHEN** the user opens the booking form in a NEW tab
- **THEN** the second tab MUST show a fresh booking wizard starting at Step 1, with no service, date, or time selected.

#### Scenario: Exclusive Service Selection via URL
- **GIVEN** a user has an active booking session with "Service A" selected
- **WHEN** the user navigates to the booking app with `?service=B` in the URL (or via `initialServiceId` prop)
- **THEN** the application MUST discard "Service A" and exclusively select "Service B"
- **AND** the user's persistent identity data MUST remain intact.

#### Scenario: Booking Reset Preservation
- **GIVEN** a user has completed a booking or triggered a reset
- **WHEN** the booking state is cleared
- **THEN** the service, date, and time MUST be reset, but the user's name, email, and phone MUST remain in the store.

#### Scenario: Navigation State
- **GIVEN** a user is on Step 3 of the booking form
- **WHEN** the user refreshes the page
- **THEN** the user MUST remain on Step 3.
- **WHEN** the user closes the tab and reopens the form
- **THEN** the user MUST start at Step 1.

