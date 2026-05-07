## MODIFIED Requirements
### Requirement: Webhook Event Processing
The dashboard SHALL expose a public endpoint to process Stripe webhook events and update booking statuses. It MUST access properties of the Stripe `event` and `session` objects (including nested objects like `metadata`) using attribute access (`getattr()` or dot notation) instead of dictionary methods like `.get()`, ensuring compatibility with Stripe Python SDK v11+.

#### Scenario: Successful Payment Webhook
- **GIVEN** a valid `checkout.session.completed` webhook event is received
- **WHEN** the `booking_id` in the session metadata matches an existing `PENDING` booking
- **THEN** the dashboard SHALL extract the metadata using attribute access
- **AND** the dashboard SHALL update the booking status to `PAID`
- **AND** the dashboard SHALL store the `stripe_payment_id`
- **AND** the Google Calendar sync SHALL be triggered for this booking