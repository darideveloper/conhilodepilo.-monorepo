# webhook Specification

## Purpose
TBD - created by archiving change implement-stripe-checkout. Update Purpose after archive.
## Requirements
### Requirement: Webhook Event Processing
The dashboard SHALL expose a public endpoint to process Stripe webhook events and update booking statuses. It MUST access properties of the Stripe `event` and `session` objects (including nested objects like `metadata`) using attribute access (`getattr()` or dot notation) instead of dictionary methods like `.get()`, ensuring compatibility with Stripe Python SDK v11+.

#### Scenario: Successful Payment Webhook
- **GIVEN** a valid `checkout.session.completed` webhook event is received
- **WHEN** the `booking_id` in the session metadata matches an existing `PENDING` booking
- **THEN** the dashboard SHALL extract the metadata using attribute access
- **AND** the dashboard SHALL update the booking status to `PAID`
- **AND** the dashboard SHALL store the `stripe_payment_id`
- **AND** the Google Calendar sync SHALL be triggered for this booking

### Requirement: Webhook Security Verification
The dashboard SHALL verify the authenticity of all incoming Stripe webhooks using the SDK's top-level (non-legacy) exception API and SHALL declare an explicit, session-independent authentication posture.

#### Scenario: Invalid Webhook Signature
- **GIVEN** a webhook request is received with an invalid `Stripe-Signature`
- **WHEN** the signature check fails
- **THEN** the dashboard SHALL catch `stripe.SignatureVerificationError` (the canonical top-level exception, not the legacy `stripe.error.*` alias)
- **AND** the dashboard SHALL return a `400 Bad Request`
- **AND** NO data SHALL be updated in the database

#### Scenario: Webhook Auth Posture
- **GIVEN** the `StripeWebhookView` class
- **WHEN** the view is loaded by Django
- **THEN** `authentication_classes` SHALL be the empty list `[]`
- **AND** the `dispatch` method SHALL be decorated with `csrf_exempt`
- **AND** a POST request without any session cookie or CSRF token SHALL reach the handler (subject only to signature verification)

### Requirement: Webhook Idempotency
The dashboard SHALL process each Stripe webhook event at most once, regardless of how many times Stripe redelivers it.

#### Scenario: Duplicate Event Delivery
- **GIVEN** a `checkout.session.completed` event with `event.id = evt_123` has already been processed
- **WHEN** Stripe redelivers the same event with `event.id = evt_123`
- **THEN** the dashboard SHALL detect the duplicate via a uniqueness constraint on stored event IDs
- **AND** the dashboard SHALL return `200 OK` without re-running the handler
- **AND** the associated `Booking` SHALL NOT be modified a second time

#### Scenario: First-Time Event Delivery
- **GIVEN** a `checkout.session.completed` event with a previously unseen `event.id`
- **WHEN** the event is received and signature-verified
- **THEN** the dashboard SHALL persist the `event.id` in the same transaction as the booking update
- **AND** the dashboard SHALL return `200 OK`

#### Scenario: Concurrent Duplicate Delivery
- **GIVEN** Stripe delivers the same event ID twice in parallel requests
- **WHEN** both requests pass signature verification simultaneously
- **THEN** exactly one SHALL successfully insert the event ID row
- **AND** the other SHALL fail with `IntegrityError` and short-circuit to `200 OK`
- **AND** the booking SHALL be updated exactly once

