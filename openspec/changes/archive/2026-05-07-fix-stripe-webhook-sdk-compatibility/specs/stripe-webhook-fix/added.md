# Spec: Stripe Webhook Fix

## ADDED Requirements

### Requirement: Stripe Webhook MUST parse events using attribute access
The `StripeWebhookView` MUST access properties of the Stripe `event` and `session` objects using dot notation (attribute access) instead of dictionary methods like `.get()`, to be compatible with Stripe Python SDK v11+.

#### Scenario: Successful checkout session completed event
- **Given** a Stripe webhook payload for `checkout.session.completed`
- **When** the `StripeWebhookView` processes the event
- **Then** it extracts the `event.id`, `event.data.object`, `session.metadata`, and `session.payment_intent` using attribute access.
- **And** it successfully updates the corresponding booking status to `PAID`.