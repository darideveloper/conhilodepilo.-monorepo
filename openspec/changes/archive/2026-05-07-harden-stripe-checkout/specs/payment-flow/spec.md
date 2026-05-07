# payment-flow Spec Delta — harden-stripe-checkout

## ADDED Requirements

### Requirement: Abandoned PRE-PAID Booking Cleanup
The dashboard SHALL release time slots held by `PENDING` bookings whose Stripe Checkout Session has expired, so that abandoned checkouts do not block other users indefinitely.

#### Scenario: Stale PENDING Booking Older Than TTL
- **GIVEN** a `Booking` with `status='PENDING'` and `created_at` older than `STRIPE_PENDING_BOOKING_TTL_HOURS` (default 24)
- **WHEN** the `cleanup_abandoned_bookings` management command runs
- **THEN** the booking SHALL be deleted
- **AND** the time slot SHALL become available to other users on the next availability query

#### Scenario: Recent PENDING Booking Within TTL
- **GIVEN** a `Booking` with `status='PENDING'` and `created_at` within the TTL window
- **WHEN** the cleanup command runs
- **THEN** the booking SHALL NOT be modified

#### Scenario: Non-PENDING Bookings Are Never Cleaned
- **GIVEN** a `Booking` with `status` of `CONFIRMED`, `PAID`, or `CANCELLED`
- **WHEN** the cleanup command runs, regardless of `created_at`
- **THEN** the booking SHALL NOT be modified

#### Scenario: Dry Run
- **GIVEN** the cleanup command is invoked with `--dry-run`
- **WHEN** matching stale bookings exist
- **THEN** the command SHALL log the booking IDs that would be deleted
- **AND** SHALL NOT mutate the database

### Requirement: Multi-Tenant Stripe Product Naming
The Stripe Checkout Session line-item name SHALL be derived from the configured `CompanyProfile.name`, not a hard-coded brand string, so the dashboard remains white-label correct.

#### Scenario: Company Profile Has A Name
- **GIVEN** `CompanyProfile.get_solo().name` returns `"Acme Spa"`
- **WHEN** a Stripe Checkout Session is created
- **THEN** the line-item `product_data.name` SHALL contain `"Acme Spa"` (exact format may include a "Reserva — " prefix or equivalent)

#### Scenario: Company Profile Name Is Blank
- **GIVEN** `CompanyProfile.get_solo().name` is empty or `None`
- **WHEN** a Stripe Checkout Session is created
- **THEN** the line-item `product_data.name` SHALL fall back to a generic, non-brand-specific string (e.g. `"Booking"`)
