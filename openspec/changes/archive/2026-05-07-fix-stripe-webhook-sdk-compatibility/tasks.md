## 1. Implementation
- [x] 1.1 Update `StripeWebhookView` in `dashboard/booking/views.py` to use attribute access for Stripe objects (`event.id`, `event.data.object`, etc.).
- [x] 1.2 Update Stripe webhook tests in `dashboard/booking/tests_stripe.py` to mock Stripe objects with attribute access correctly.
- [x] 1.3 Run Stripe-related tests in the dashboard to verify the webhook processes correctly and idempotency works as expected.