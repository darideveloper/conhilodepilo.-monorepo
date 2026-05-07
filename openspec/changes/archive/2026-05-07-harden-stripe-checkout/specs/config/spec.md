# config Spec Delta — harden-stripe-checkout

## MODIFIED Requirements

### Requirement: Environment-Driven Configuration
The system SHALL use environment variables for all Stripe-related credentials and operational tunables, and SHALL document every required variable in the committed `.env.example` files so that a fresh checkout can be configured without reading source code.

#### Scenario: Production Configuration
- **GIVEN** the system is running in a production environment
- **WHEN** Stripe operations are performed
- **THEN** the dashboard SHALL use `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` from the environment variables
- **AND** sensitive keys SHALL NOT be stored in the database or committed to version control

#### Scenario: Env Example Completeness
- **GIVEN** a fresh checkout of the repository
- **WHEN** a developer inspects `dashboard/.env.example`
- **THEN** the file SHALL contain placeholder entries for: `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `LANDING_URL`, and `STRIPE_PENDING_BOOKING_TTL_HOURS`
- **AND** each entry SHALL have either an empty placeholder value or a safe default suitable for local development

#### Scenario: Pending Booking TTL Setting
- **GIVEN** the dashboard is starting up
- **WHEN** Django settings are loaded
- **THEN** `settings.STRIPE_PENDING_BOOKING_TTL_HOURS` SHALL be read from the environment
- **AND** SHALL default to `24` when the variable is unset
