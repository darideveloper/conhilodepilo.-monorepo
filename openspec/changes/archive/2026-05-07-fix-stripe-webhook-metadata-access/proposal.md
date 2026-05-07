# Proposal: Fix Stripe Webhook Metadata Access

## Why
In production, when a user completes a booking payment, the Stripe webhook fails with an `AttributeError: get` on the `session.metadata.get('booking_id')` line. This is a continuation of the Stripe SDK v11+ compatibility issue. In the new SDK version, Stripe objects (including nested ones like `metadata`) are instantiated as `StripeObject` instances, not native Python dictionaries, meaning the `.get()` dictionary method is unavailable and crashes the process.

## What Changes
- Update `StripeWebhookView` in `dashboard/booking/views.py` to use `getattr(session.metadata, 'booking_id', None)` instead of `session.metadata.get('booking_id')`.
- Update any related test mock setups in `dashboard/booking/tests_stripe.py` if they rely on dictionary methods, to ensure tests accurately represent the behavior of the SDK and pass.

## Impact
- Affected specs: `webhook`
- Affected code: `dashboard/booking/views.py`, `dashboard/booking/tests_stripe.py`