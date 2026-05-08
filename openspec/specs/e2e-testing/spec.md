# e2e-testing Specification

## Purpose
TBD - created by archiving change add-playwright-e2e. Update Purpose after archive.
## Requirements
### Requirement: E2E Project Structure
The monorepo SHALL contain a top-level `e2e/` directory that is a self-contained Playwright + TypeScript project with its own `package.json` and `playwright.config.ts`, independent of `dashboard/`, `booking/`, and `landing/`.

#### Scenario: Isolated dependency graph
- **WHEN** a developer runs `npm install` inside `e2e/`
- **THEN** Playwright, its browser binaries, and TypeScript are installed only in `e2e/node_modules`
- **AND** none of those packages appear in `booking/` or `landing/` node_modules.

#### Scenario: Running the suite from the project root
- **WHEN** a developer runs `cd e2e && npx playwright test`
- **THEN** all example specs execute against the locally-running dev services
- **AND** the command exits 0 when all services are up and accessible.

---

### Requirement: Multi-Project Playwright Configuration
`e2e/playwright.config.ts` SHALL define at least four named projects — `booking`, `dashboard`, `landing`, and `integrations` — each targeting its corresponding base URL and test directory.

#### Scenario: Running a single project
- **WHEN** a developer runs `npx playwright test --project=booking`
- **THEN** only specs under `tests/booking/` execute.

#### Scenario: Base URL from environment variable
- **WHEN** `BOOKING_URL` is set in `e2e/.env`
- **THEN** the `booking` project uses that value as `baseURL`
- **AND** falls back to `https://booking.conhilodepilo` when the variable is absent.

#### Scenario: Invalid SSL certificate (portless)
- **GIVEN** all services are served over HTTPS via portless with locally-invalid SSL certificates
- **WHEN** any spec navigates to a service URL
- **THEN** Playwright MUST NOT abort with a certificate error
- **AND** the global `use` config SHALL set `ignoreHTTPSErrors: true`.

---

### Requirement: Page Object Model Layer
The `e2e/pages/` directory SHALL provide one Page Object class per major UI surface, encapsulating all locators and user-facing actions for that surface so that spec files contain no raw CSS selectors or `page.locator()` calls.

#### Scenario: Using a POM in a spec
- **GIVEN** a spec imports `BookingFlowPage` from `e2e/pages/booking/BookingFlowPage.ts`
- **WHEN** the spec calls `flow.open()`
- **THEN** the browser navigates to the booking root URL
- **AND** the spec can call named action methods such as `flow.selectService(id)` without knowing the underlying selector.

#### Scenario: Selector update is local to the POM
- **GIVEN** the booking service-selection markup changes its CSS class
- **WHEN** a developer updates the selector in `BookingFlowPage.ts`
- **THEN** all specs that use `BookingFlowPage` pick up the fix automatically with no changes to spec files.

---

### Requirement: Auth Fixture
The `e2e/fixtures/` directory SHALL export a composed `test` object that extends the Playwright base fixture with an `adminCredentials` fixture providing the Django admin username and password. Every spec SHALL import `test` and `expect` from `e2e/fixtures/base.ts` rather than directly from `@playwright/test`.

#### Scenario: Admin credentials from environment
- **GIVEN** `DASHBOARD_ADMIN_USER` and `DASHBOARD_ADMIN_PASS` are set in `e2e/.env`
- **WHEN** a spec destructures `{ adminCredentials }` from the test
- **THEN** the fixture provides those values for the duration of the test.

#### Scenario: Default credentials for local dev
- **GIVEN** `DASHBOARD_ADMIN_USER` and `DASHBOARD_ADMIN_PASS` are not set
- **WHEN** a spec uses the `adminCredentials` fixture
- **THEN** it falls back to `admin` / `admin` (standard Django dev-server defaults).

---

### Requirement: API Helper Utilities
The `e2e/helpers/api.ts` module SHALL expose typed wrapper functions around the Dashboard REST API using Playwright's `APIRequestContext`, which inherits `ignoreHTTPSErrors: true` from the project config. Helpers cover the public read and write endpoints only: `createBooking`, `fetchServices`, `fetchAvailableSlots`.

#### Scenario: Creating a booking without UI interaction
- **GIVEN** an integration test needs a booking to exist in the dashboard
- **WHEN** the test calls `createBooking(request, payload)`
- **THEN** the booking is created via `POST /api/bookings/`
- **AND** the test can proceed to validate dashboard UI behaviour without performing the full booking wizard flow.

#### Scenario: TLS bypass for local HTTPS
- **GIVEN** the dashboard is served over HTTPS with a self-signed cert
- **WHEN** `fetchServices(request)` or any helper is called
- **THEN** the request succeeds without TLS errors because `APIRequestContext` inherits `ignoreHTTPSErrors: true`.

---

### Requirement: Test Directory Organisation
Tests SHALL be organised under `e2e/tests/` by domain: `booking/`, `dashboard/`, and `integrations/`. Each domain directory MUST contain at least one example spec (`*.example.spec.ts`) that demonstrates the harness is functional.

#### Scenario: Example spec for booking domain
- **GIVEN** the booking service is running
- **WHEN** `booking/booking-flow.example.spec.ts` runs
- **THEN** the browser opens the booking root URL
- **AND** the spec asserts that `[data-slot="card"]` is visible after React hydration, proving basic connectivity.

#### Scenario: Example spec for dashboard domain
- **GIVEN** the dashboard service is running
- **WHEN** `dashboard/admin-login.example.spec.ts` runs
- **THEN** the browser navigates to `/admin/` (which redirects to the login form)
- **AND** the spec asserts `#login-form`, `#id_username`, `#id_password`, and the `Iniciar sesión` button are visible.

#### Scenario: Example spec for integrations domain
- **GIVEN** both dashboard and booking services are running with at least one service and available slot
- **WHEN** `integrations/booking-to-dashboard.example.spec.ts` runs
- **THEN** the spec creates a booking via `createBooking(request, payload)` with a unique `clientName`
- **AND** logs into the Django admin using the `LoginPage` POM
- **AND** asserts the booking row (matched by `clientName`) is visible in the `#result_list` table.

#### Scenario: Graceful skip when no data is available
- **GIVEN** the dashboard has no services or no availability configured
- **WHEN** the integration example spec runs
- **THEN** the spec calls `test.skip()` with a human-readable message
- **AND** the suite exits 0.

---

### Requirement: Environment Configuration
`e2e/.env.example` SHALL document every environment variable required to run the suite, with safe placeholder values. The actual `e2e/.env` file SHALL be git-ignored.

#### Scenario: Onboarding a new developer
- **GIVEN** a developer clones the repo and copies `e2e/.env.example` to `e2e/.env`
- **WHEN** they fill in the variables and run `npx playwright test --project=booking`
- **THEN** the suite runs without requiring undocumented configuration.

---

### Requirement: Integration Test Graceful Skip
Specs that depend on data or services that may not be present SHALL skip themselves gracefully rather than failing.

#### Scenario: No services in the database
- **GIVEN** the dashboard database has no services configured
- **WHEN** the integration example spec runs
- **THEN** Playwright marks the test as skipped with a human-readable message
- **AND** the suite still exits 0.

