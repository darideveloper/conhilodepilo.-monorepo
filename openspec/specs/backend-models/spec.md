# backend-models Specification

## Purpose
TBD - created by archiving change group-services-by-type. Update Purpose after archive.
## Requirements
### Requirement: Service Categorization
The system MUST allow grouping service categories (Event Types) into broader groups to facilitate filtering and specialization of the booking flow.

#### Scenario: Assign Group to Event Type
- **Given** an existing `EventType` "Depilación con hilo".
- **And** a group "Salon Services" with ID 1.
- **When** the admin assigns "Salon Services" to "Depilación con hilo".
- **Then** the API MUST return `group_id: 1` for that event type.

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

