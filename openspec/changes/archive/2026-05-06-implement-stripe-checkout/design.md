# Design: Stripe Implementation

## Architecture Overview

The system uses Stripe Checkout (hosted payment page) to minimize PCI compliance burden and simplify the frontend integration.

### Booking Flow Sequence

1.  **Selection**: User selects services in the Booking App.
2.  **Submission**: User submits the form.
3.  **Dashboard Validation**:
    - `CreateBookingView` checks availability.
    - It calculates the total price by summing `Event.price` for all selected services.
    - It retrieves the `currency` from the `CompanyProfile` (singleton).
    - It checks if any service belongs to an `EventType` with `payment_model="PRE-PAID"`.
4.  **Conditional Path**:
    - **Path A (Post-Paid)**:
        - `Booking.status` set to `CONFIRMED`.
        - API returns `{ "payment_required": false }`.
        - Frontend shows success message.
    - **Path B (Pre-Paid)**:
        - `Booking.status` set to `PENDING`.
        - Dashboard creates a Stripe Checkout Session:
            - `amount`: Total price in cents (converted based on currency).
            - `currency`: From `CompanyProfile`.
            - `metadata`: `{"booking_id": booking.id}`.
            - `success_url`: `${LANDING_URL}/success?session_id={CHECKOUT_SESSION_ID}` (where `LANDING_URL` is a dashboard setting).
            - `cancel_url`: `${LANDING_URL}/cancel`.
        - API returns `{ "payment_required": true, "checkout_url": session.url }`.
        - Frontend (within iframe) clears `useBookingStore` and then redirects the parent window or current context via `window.location.href`.

### State Management & Iframe Escape
Since the success/cancel pages are on the `landing/` domain, the user effectively "escapes" the iframe after the Stripe payment process. To ensure no stale data remains in the `booking/` store, the `BookingForm` component MUST clear the Zustand store immediately before initiating the redirect to Stripe.

### Currency Handling
Stripe expects amounts in the smallest currency unit (e.g., cents for EUR/USD). The system MUST correctly multiply the `Event.price` (Decimal) by the appropriate factor (usually 100) before sending it to Stripe.

## Data Schema Updates

### Existing Models (No changes needed, but utilization will increase)
- `EventType.payment_model`: `PRE-PAID` or `POST-PAID`.
- `Booking.status`: `PENDING`, `CONFIRMED`, `PAID`, `CANCELLED`.
- `Booking.stripe_payment_id`: Stores the Stripe Session or Charge ID.

## Webhook Security

The `StripeWebhookView` will use the official `stripe` Python library to verify the `Stripe-Signature` header against the `STRIPE_WEBHOOK_SECRET`. This prevents spoofing.

## Frontend State Management

The `useBookingStore` (Zustand) should be cleared upon arrival at the success page to prevent duplicate submissions or stale UI states.
