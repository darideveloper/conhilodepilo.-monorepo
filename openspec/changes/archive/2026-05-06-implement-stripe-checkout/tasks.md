# Tasks: Implement Stripe Checkout

## Phase 1: Dashboard Infrastructure & Logic

- [x] **Install Stripe library**: Add `stripe` to `dashboard/requirements.txt` and install it.
- [x] **Configure Environment**: Update `dashboard/.env.example` with placeholders for `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, and `STRIPE_WEBHOOK_SECRET`.
- [x] **Expose Payment Model**: Update `dashboard/booking/serializers.py` to include `payment_model` in the `EventTypeSerializer`.
- [x] **Implement Stripe Utility**: Create `dashboard/utils/stripe_utils.py` with a helper to create Checkout Sessions (handling currency conversion to cents).
- [x] **Update CreateBookingView**:
    - [x] Logic to check if any service is `PRE-PAID`.
    - [x] Calculate total amount and fetch currency from `CompanyProfile`.
    - [x] Create Stripe session with `booking_id` in metadata.
    - [x] Return `payment_required: true` and `checkout_url`.
    - [x] Set `Booking.status` to `CONFIRMED` for `POST-PAID` only bookings.
- [x] **Implement Webhook View**: Create `dashboard/booking/views.py:StripeWebhookView`.
    - [x] Add URL pattern in `dashboard/project/urls.py`.
    - [x] Add logic to verify signature, update booking status to `PAID`, and store `stripe_payment_id`.
- [x] **Refine GCal Signals**: Update `dashboard/booking/signals.py` to skip sync if status is `PENDING`.

## Phase 2: Frontend Integration

- [x] **Update Booking Submission**: Modify `booking/src/components/organisms/BookingForm.tsx`.
    - [x] Add handling for `payment_required` and `checkout_url` in `handleSubmit`.
    - [x] Implement store reset (`resetStore()`) right before `window.location.href` redirect.
    - [x] Add error handling for failed session creation.
- [x] **Create Landing Success Page**: Add `landing/src/pages/success.astro`.
    - [x] Design a friendly "Payment Successful" message following the landing page aesthetic.
    - [x] Add a "Return to Home" button.
- [x] **Create Landing Cancel Page**: Add `landing/src/pages/cancel.astro`.
    - [x] Design a message informing the user that the payment was not completed.
    - [x] Add a button to return to the booking section.

## Phase 3: Validation

- [x] **Dashboard Tests**:
    - [x] Unit test for Stripe session creation (mocked).
    - [x] Integration test for webhook processing (using Stripe CLI or mock payload).
- [x] **Frontend Manual Test**:
    - [x] Verify `POST-PAID` flow shows success message directly.
    - [x] Verify `PRE-PAID` flow redirects to Stripe.
- [x] **End-to-End**:
    - [x] Complete a full payment flow using Stripe Test Cards.
