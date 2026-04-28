# api-contracts Specification

## Purpose
TBD - created by archiving change finalize-booking-integration. Update Purpose after archive.
## Requirements
### Requirement: Create Booking Endpoint
The system MUST provide an API endpoint to create a new booking record.

#### Scenario: Successful booking creation
- **WHEN** a valid JSON payload containing user details, selected date/time, and services is submitted
- **THEN** the API MUST create a booking record with status PENDING, accurately calculate the end time based on the selected services, and return a success response.

#### Scenario: Invalid booking payload
- **WHEN** a booking payload is submitted with an unavailable time slot or missing required fields
- **THEN** the API MUST return an HTTP 400 Bad Request with a structured error message indicating the specific validation failure.

