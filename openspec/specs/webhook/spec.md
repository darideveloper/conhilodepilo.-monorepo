# webhook Specification

## Purpose
TBD - created by archiving change implement-stripe-checkout. Update Purpose after archive.
## Requirements
### Requirement: Webhook Event Processing
The backend SHALL expose a public endpoint to process Stripe webhook events and update booking statuses.

#### Scenario: Successful Payment Webhook
- **GIVEN** a valid `checkout.session.completed` webhook event is received
- **WHEN** the `booking_id` in the session metadata matches an existing `PENDING` booking
- **THEN** the backend SHALL update the booking status to `PAID`
- **AND** the backend SHALL store the `stripe_payment_id`
- **AND** the Google Calendar sync SHALL be triggered for this booking

### Requirement: Webhook Security Verification
The backend SHALL verify the authenticity of all incoming Stripe webhooks.

#### Scenario: Invalid Webhook Signature
- **GIVEN** a webhook request is received with an invalid `Stripe-Signature`
- **WHEN** the signature check fails
- **THEN** the backend SHALL return a `400 Bad Request`
- **AND** NO data SHALL be updated in the database

