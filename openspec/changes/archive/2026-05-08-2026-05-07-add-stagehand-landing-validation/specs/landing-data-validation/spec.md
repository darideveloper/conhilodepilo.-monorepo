# Spec: Landing Data Validation (Stagehand)

## ADDED Requirements

### Requirement: Service Category Rendering Verification
The Stagehand test SHALL verify that the service categories and their nested services displayed on the landing page match the data provided by the Dashboard API.

#### Scenario: Verify Service Categories and Nested Services
- **Given** the Landing Page is running and connected to a Dashboard instance with active `EventType` and `Event` records.
- **When** the Stagehand agent navigates to the `#servicios` section.
- **Then** it should extract a list of categories where each entry has a `categoryName`, an `imageSrc`, and a list of `services` (title, price, duration).
- **And** the data must correspond to the `EventType` objects where `group_id` is NOT the course group.

### Requirement: Service Selection Interaction
The test SHALL verify that selecting a service within a category updates the displayed price and duration.

#### Scenario: Verify Price Update on Click
- **Given** a `CategoryCard` with multiple services.
- **When** the Stagehand agent clicks on a service button different from the default one.
- **Then** the displayed price and duration MUST update to match the newly selected service.

### Requirement: Course Filtering and Navigation Verification
The test SHALL ensure that only services belonging to the `COURSES_GROUP_ID` appear in the "Cursos" section and that they link correctly to the booking app.

#### Scenario: Verify Course Rendering and Links
- **Given** the `#cursos` section on the landing page.
- **When** the Stagehand agent extracts course data.
- **Then** it must include a `bookingUrl` for each course.
- **And** that `bookingUrl` MUST follow the format `/booking/[id]` where `id` is the service ID from the dashboard.

### Requirement: Dashboard Media Integrity
The test MUST verify that all images sourced from the Dashboard are correctly resolved and accessible.

#### Scenario: Check Dashboard Image Accessibility
- **Given** images rendered in `CategoryCard` or `CourseCard`.
- **When** their `src` attribute contains the `PUBLIC_API_URL`.
- **Then** the URL must use the correct protocol (matching the site) and return a `200 OK` status.
