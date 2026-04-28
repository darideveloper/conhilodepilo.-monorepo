## ADDED Requirements
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
