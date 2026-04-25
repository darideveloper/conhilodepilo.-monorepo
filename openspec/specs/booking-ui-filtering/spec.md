# booking-ui-filtering Specification

## Purpose
TBD - created by archiving change group-services-by-type. Update Purpose after archive.
## Requirements
### Requirement: Group-Based UI Locking
The booking interface SHALL lock the available service categories based on the group of the first prefilled service detected in the URL.

#### Scenario: Locked View for Courses
- **Given** a user visits the booking page with `?service=6` (where service 6 belongs to "Courses" group ID 2).
- **When** the page loads.
- **Then** the "Service Category" dropdown MUST ONLY show categories belonging to group ID 2.
- **And** even if the user removes service 6 from the selection, the dropdown MUST REMAIN filtered to group ID 2.

### Requirement: Unfiltered View
The booking interface SHALL show all service categories when no prefilled service is provided.

#### Scenario: Unfiltered View
- **Given** a user visits the booking page with no URL parameters.
- **When** the page loads.
- **Then** the "Service Category" dropdown MUST show ALL categories.

