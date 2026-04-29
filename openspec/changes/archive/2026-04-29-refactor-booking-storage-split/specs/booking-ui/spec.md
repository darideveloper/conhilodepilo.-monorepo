# Spec: Hybrid Booking Data Persistence

## ADDED Requirements

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
