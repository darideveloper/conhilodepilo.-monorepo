## 1. Implementation
- [x] 1.1 Update `booking_id` retrieval in `dashboard/booking/views.py` inside `StripeWebhookView.post` to use `getattr(session.metadata, 'booking_id', None)`.
- [x] 1.2 Verify and adjust mock Stripe event configurations in `dashboard/booking/tests_stripe.py` to ensure they don't break with the new attribute access (they should already be `MagicMock` from the previous fix, but need a quick check).
- [x] 1.3 Run `python manage.py test booking.tests_stripe` in the `dashboard` virtual environment to confirm all tests pass successfully.