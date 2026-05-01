# Stripe Integration Setup Guide

This guide provides the necessary steps to configure Stripe for the Con Hilo Depilo booking system. Follow these instructions when setting up a new production environment or migrating to a different Stripe account.

## 1. API Credentials Setup

1.  Log in to the [Stripe Dashboard](https://dashboard.stripe.com/).
2.  Navigate to **Developers > API keys**.
3.  **Public Key**: Copy the "Publishable key" and set it as `STRIPE_PUBLIC_KEY`.
4.  **Secret Key**:
    *   It is recommended to use **Restricted keys** for better security.
    *   Click "Create restricted key".
    *   Give it a name (e.g., "Booking System Key").
    *   Grant **Write** access to `Checkout Sessions`.
    *   Grant **Read** access to `PaymentIntents`.
    *   Copy the generated key and set it as `STRIPE_SECRET_KEY`.

## 2. Webhook Configuration

Webhooks are critical for updating the booking status from `PENDING` to `PAID` after a successful payment.

1.  Go to **Developers > Webhooks**.
2.  Click **Add an endpoint**.
3.  **Endpoint URL**: `https://api.yourdomain.com/api/stripe/webhook/`
    *   *Note: Ensure the URL ends with a trailing slash.*
4.  **Select events**: Add `checkout.session.completed`.
5.  **Signing Secret**: After creating the endpoint, click "Reveal" under "Signing secret".
6.  Copy this value and set it as `STRIPE_WEBHOOK_SECRET`.

## 3. Branding & Customer Experience

To ensure a seamless transition for users, configure the Stripe Checkout appearance:

1.  Navigate to **Settings > Branding**.
    *   **Icon/Logo**: Upload the company logo.
    *   **Brand Color**: Set to `#ee5837` (or the current primary color).
    *   **Accent Color**: Set a matching secondary color.
2.  Navigate to **Settings > Public details**.
    *   Verify the **Public business name**, **Support email**, and **Support phone**. These appear on the Stripe-hosted checkout page.

## 4. Legal & Compliance

Stripe Checkout requires valid legal links to be visible:

1.  Navigate to **Settings > Checkout settings**.
2.  Ensure **Privacy Policy** and **Terms of Service** URLs are provided.
    *   The Privacy Policy should match the `privacy_policy_url` defined in the Django `CompanyProfile` model.

## 5. Environment Variables Summary

Ensure the following variables are set in your backend environment (`.env` file):

| Variable | Description | Source |
| :--- | :--- | :--- |
| `STRIPE_PUBLIC_KEY` | Public API Key | Developers > API Keys |
| `STRIPE_SECRET_KEY` | Secret/Restricted Key | Developers > API Keys |
| `STRIPE_WEBHOOK_SECRET` | Webhook Signing Secret | Developers > Webhooks |
| `LANDING_URL` | Base URL of the Landing Page | e.g., `https://yourdomain.com` |

## 6. Local Development & Testing

To test webhooks on your local machine:

1.  Install the [Stripe CLI](https://stripe.com/docs/stripe-cli).
2.  Login: `stripe login`.
3.  Start forwarding:
    ```bash
    stripe listen --forward-to localhost:8000/api/stripe/webhook/
    ```
4.  The CLI will output a local webhook signing secret (starts with `whsec_`).
5.  Update your `backend/.env.dev` with this local secret.
6.  Perform a booking in the frontend; the CLI will log the events as they are received.

### Test Cards
Use the following card numbers in **Test Mode**:
*   **Success**: `4242 4242 4242 4242` (Any future expiry, any CVC)
*   **Decline**: [See Stripe Test Cards documentation](https://stripe.com/docs/testing#cards)
