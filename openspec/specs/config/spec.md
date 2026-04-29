# config Specification

## Purpose
TBD - created by archiving change implement-stripe-checkout. Update Purpose after archive.
## Requirements
### Requirement: Environment-Driven Configuration
The system SHALL use environment variables for all Stripe-related credentials to ensure security and portability.

#### Scenario: Production Configuration
- **GIVEN** the system is running in a production environment
- **WHEN** Stripe operations are performed
- **THEN** the backend SHALL use `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` from the environment variables
- **AND** sensitive keys SHALL NOT be stored in the database or committed to version control

