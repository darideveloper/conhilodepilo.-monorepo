# landing-ui Specification

## Purpose
TBD - created by archiving change limit-coursecard-description. Update Purpose after archive.
## Requirements
### Requirement: Course Card Description Limitation
The Course Card component on the Landing page MUST limit its displayed description to a maximum of 3 lines to maintain layout consistency. The truncation MUST be applied visually (e.g., using CSS line-clamp) to ensure that any underlying Markdown or HTML structures remain intact and are not broken mid-tag.

#### Scenario: Rendering a long markdown description
- **Given** a Course Card with a markdown description that renders to more than 3 lines of text
- **When** the card is displayed on the frontend
- **Then** the text should be truncated at the end of the third line with an ellipsis (`...`)
- **And** no HTML elements should be left unclosed or broken due to the truncation

### Requirement: Service Category Filtering
The landing page MUST identify and separate "Courses" from "Salon Services" using the `group_id` field provided by the dashboard API. The specific IDs used for filtering MUST be configurable via environment variables.

#### Scenario: Identifying Courses
- **Given** a list of service categories from the API
- **And** the `PUBLIC_COURSES_GROUP_ID` environment variable
- **When** filtering for courses
- **Then** the application MUST select categories where `group_id` matches the value of `PUBLIC_COURSES_GROUP_ID`
- **And** map their services to the `Course` type

#### Scenario: Identifying Salon Services
- **Given** a list of service categories from the API
- **And** the `PUBLIC_COURSES_GROUP_ID` environment variable
- **When** filtering for regular services
- **Then** the application MUST exclude all categories where `group_id` matches `PUBLIC_COURSES_GROUP_ID`
- **And** maintain their `ServiceCategory` structure

### Requirement: Landing Page Branding
The success and cancellation landing pages SHALL display the brand logo to maintain visual identity.

#### Scenario: Display Logo on Success Page
- **GIVEN** a user is on the `/success` page
- **THEN** the brand logo (`/logo.webp`) SHALL be displayed at the top of the confirmation card, replacing the status icon circle.

#### Scenario: Display Logo on Cancel Page
- **GIVEN** a user is on the `/cancel` page
- **THEN** the brand logo (`/logo.webp`) SHALL be displayed at the top of the status card, replacing the status icon circle.

### Requirement: Brand Text Highlighting
The landing site SHALL use the brand's primary color for bold text highlights to reinforce visual identity.

#### Scenario: Bold text in content
- **GIVEN** any component or MDX content using `<strong>` or `**bold**`
- **THEN** the text SHALL be rendered in the `brand-primary` color
- **AND** have a bold font weight.

