# Implement Stripe Checkout

This proposal details the full implementation of Stripe payments for the booking system. It supports both `PRE-PAID` and `POST-PAID` services, ensuring that users are redirected to Stripe for payment when necessary while maintaining a direct confirmation path for unpaid services.

## Problem
The current system has the data models for payment models but lacks the actual integration logic. Bookings are always created as `PENDING` and never transition to `PAID` or `CONFIRMED` through an automated flow.

## Proposed Solution

### 1. Dashboard: Payment Logic & Webhooks
- **Dependency**: Add `stripe` to `requirements.txt`.
- **Checkout Logic**: Update `CreateBookingView` to:
    - Identify if any selected service belongs to an `EventType` with `payment_model="PRE-PAID"`.
    - If `PRE-PAID`, create a Stripe Checkout Session using the total price of all services.
    - Return `payment_required: true` and the `checkout_url`.
    - If all are `POST-PAID`, set the booking status to `CONFIRMED` and return `payment_required: false`.
- **Webhook**: Implement a `StripeWebhookView` to listen for `checkout.session.completed`.
    - Verify the webhook signature using `STRIPE_WEBHOOK_SECRET`.
    - Extract the `booking_id` from the session metadata.
    - Update the `Booking` status to `PAID` and store the `stripe_payment_id`.
- **Signals**: Adjust Google Calendar sync signals to only trigger for `CONFIRMED` or `PAID` bookings.

### 2. Frontend: Conditional Flow
- **Booking Submission**: Update `BookingForm.tsx` to handle the new API response.
    - On `payment_required: true`, clear the local `useBookingStore` and then perform a hard redirect to the `checkout_url`.
    - On `payment_required: false`, show the existing local success message.
- **Success & Cancel Pages (Landing Service)**: Create new Astro pages in the `landing/` service:
    - `landing/src/pages/success.astro`: Display a full-page confirmation message.
    - `landing/src/pages/cancel.astro`: Display a cancellation message and a link back to the booking section.

### 3. Configuration
- All Stripe keys (`STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`) and the `LANDING_URL` will be managed via environment variables in `dashboard/project/settings.py`.

## Impact
- **Database**: `Booking` status will correctly reflect the payment state.
- **User Experience**: Seamless transition between the booking form and Stripe checkout.
- **Operational**: Automatic confirmation of paid appointments in Google Calendar.
