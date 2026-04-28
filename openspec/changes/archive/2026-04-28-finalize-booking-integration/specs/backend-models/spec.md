## ADDED Requirements
### Requirement: Privacy Policy Configuration
The system MUST allow an administrator to configure a privacy policy URL for the company.

#### Scenario: Fetching company profile
- **WHEN** the company configuration is requested
- **THEN** the configuration MUST include a valid `privacy_policy_url`.

### Requirement: Booking Special Requests Storage
The system MUST store any special requests made by the user during the booking process.

#### Scenario: Persisting a booking
- **WHEN** a user provides special requests in the contact form
- **THEN** the system MUST save them in the corresponding booking record.
