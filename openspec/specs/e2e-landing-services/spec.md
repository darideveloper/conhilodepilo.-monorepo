# e2e-landing-services Specification

## Purpose
TBD - created by archiving change add-e2e-landing-services-test. Update Purpose after archive.
## Requirements
### Requirement: Landing Services Section Card Count
The E2E landing test suite SHALL verify that the `#servicios` section renders one `CategoryCard` (`article` element) per non-courses service category returned by `GET /api/services/`.

#### Scenario: Card count matches API response
- **GIVEN** the dashboard has N service categories that do not belong to the courses group
- **WHEN** the landing page is loaded and the `#servicios` section is visible
- **THEN** exactly N `article` elements are rendered inside `#servicios`

#### Scenario: Graceful skip when no services are available
- **GIVEN** the dashboard has zero non-courses service categories
- **WHEN** the landing services test suite runs
- **THEN** each test calls `test.skip()` with a human-readable message explaining the missing data
- **AND** the Playwright suite exits with code 0

---

### Requirement: CategoryCard Dashboard Data Fields
The E2E landing test suite SHALL verify that the first `CategoryCard` in the `#servicios` grid renders the category image, name, and description sourced from the dashboard API, with no static placeholder fallbacks substituted for present data.

#### Scenario: Category image renders from dashboard media
- **GIVEN** the first non-courses service category has an uploaded image in the dashboard
- **WHEN** the landing page is loaded
- **THEN** an `img` element is visible inside the first `article` card's image area
- **AND** the `img` element's `src` attribute is a non-empty string (not a blank or data-URI placeholder)

#### Scenario: Gray placeholder is absent when image is configured
- **GIVEN** the first category has a non-null `image` in the API response
- **WHEN** the landing page is loaded
- **THEN** the gray fallback `div` (with `bg-gray-100` class) is NOT the visible element inside the image area

#### Scenario: Category name matches API response
- **GIVEN** the dashboard returns the first category with a specific `name` field value
- **WHEN** the landing page is loaded
- **THEN** the `h3` element inside the first `article` card contains text equal to `category.name`

#### Scenario: Category description renders non-empty content
- **GIVEN** the first category has a non-null `description` field in the API response
- **WHEN** the landing page is loaded
- **THEN** the description element inside the first `article` card has non-empty text content (rendered from Markdown)

---

### Requirement: Service Pill Buttons
The E2E landing test suite SHALL verify that each `CategoryCard` renders exactly one pill button per service in that category, that the first pill is pre-selected on initial load, and that clicking a different pill updates the selected state.

#### Scenario: Pill button count matches API services
- **GIVEN** the first category has N services in the `services` array of the API response
- **WHEN** the landing page is loaded and React has hydrated the `CategoryShowcase` island
- **THEN** the first `article` card contains exactly N pill buttons inside the "Servicios disponibles" section

#### Scenario: First service pill is pre-selected on load
- **GIVEN** the landing page has loaded and React has hydrated
- **WHEN** the first `article` card is inspected
- **THEN** the first service pill button has the selected visual state (background matches the `brand-primary` color)
- **AND** no other pill button in the same card has the selected state

#### Scenario: Clicking a different pill updates the selection
- **GIVEN** the first card has at least two service pill buttons
- **AND** the first pill is currently selected
- **WHEN** the user clicks the second pill button
- **THEN** the second pill gains the selected visual state
- **AND** the first pill loses the selected visual state

---

### Requirement: Selected Service Price and Duration
The E2E landing test suite SHALL verify that the price and duration displayed in the `CategoryCard` footer match the currently selected service's values from the API, and that they update when a different pill is selected.

#### Scenario: Price shown for the default (first) selected service
- **GIVEN** the landing page has loaded with the first service pre-selected
- **WHEN** the price element in the first card's footer is inspected
- **THEN** it contains text matching the first service's `price` field from the API (e.g., `€XX.XX` — non-empty)

#### Scenario: Duration shown for the default selected service
- **GIVEN** the landing page has loaded with the first service pre-selected
- **WHEN** the duration element in the first card's footer is inspected
- **THEN** it contains text in the form `{duration} min` matching the first service's `duration` field from the API

#### Scenario: Price and duration update after clicking a different pill
- **GIVEN** the first card has at least two services with different prices or durations
- **WHEN** the user clicks the second service pill button
- **THEN** the price element updates to reflect the second service's `price` from the API
- **AND** the duration element updates to reflect the second service's `duration` from the API

---

### Requirement: Reservar CTA Navigation
The E2E landing test suite SHALL verify that the "Reservar" button in a `CategoryCard` navigates the browser to `/booking/{service.id}`, where `service.id` is the ID of the service currently selected in that card.

#### Scenario: Clicking Reservar navigates to the service booking page
- **GIVEN** the first `CategoryCard` has a service selected (first service, selected by default)
- **WHEN** the user clicks the "Reservar" button
- **THEN** the browser navigates to a URL whose path matches `/booking/{id}`
- **AND** the `id` segment equals the selected service's `id` from the API response

