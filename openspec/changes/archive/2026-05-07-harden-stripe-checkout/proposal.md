# Harden Stripe Checkout Integration

This proposal closes the gaps surfaced by the post-implementation audit of `implement-stripe-checkout`. The original change delivered the happy path, but several correctness, security, and operational issues remain that would cause failures or stale state in production.

## Problem

The current Stripe integration has the following defects:

1. **Non-canonical signature exception import.** `dashboard/booking/views.py` catches `stripe.error.SignatureVerificationError`. In the installed `stripe` 15.x SDK this still resolves (it is a backwards-compat alias of `stripe.SignatureVerificationError`), so the path is *not* broken at runtime today. However, the `stripe.error` namespace is the legacy location and the SDK has been migrating callers to the top-level `stripe.*` exceptions; future major versions are expected to drop the alias. Standardizing on `stripe.SignatureVerificationError` removes a latent upgrade hazard and aligns with current Stripe SDK docs. The same path appears in `dashboard/booking/tests_stripe.py`.
2. **Implicit webhook CSRF/auth posture.** `StripeWebhookView` is an `APIView` with `AllowAny`, but `DEFAULT_AUTHENTICATION_CLASSES` includes `SessionAuthentication`. Webhooks pass today only because Stripe sends no session cookie. The view does not declare `@csrf_exempt` or `authentication_classes = []`, so a future change (e.g. forcing CSRF, adding middleware) could silently break webhook delivery.
3. **No webhook idempotency.** Stripe retries `checkout.session.completed` on transient failures and at-least-once semantics. The current view re-runs blindly; the only safeguard is the `status == 'PENDING'` guard, which is incidental rather than designed.
4. **Phantom `PENDING` bookings hold slots.** `CreateBookingView` writes a `PENDING` `Booking` row before creating the Stripe Checkout Session. If the user abandons checkout (closes tab, never pays), the row persists indefinitely and blocks the slot from other users. Stripe Checkout Sessions expire after 24 hours; abandoned bookings should expire with them. **The `Booking` model currently has no `created_at` timestamp** (`dashboard/booking/models.py:206-233`), so a cleanup query has no field to filter on — this proposal must add one.
5. **`.env.example` was never actually updated.** Despite the task being checked off in the original change, `dashboard/.env.example` still contains only `ENV=dev`. New developers cannot bootstrap Stripe locally without reading the source.
6. **Hard-coded Stripe product name.** `dashboard/utils/stripe_utils.py` hard-codes `'Reserva - Con Hilo Depilo'` as the line-item name. This is incorrect for any white-label deployment of the dashboard.
7. **No documented end-to-end validation.** The original `tasks.md` left the live Stripe-CLI test card flow as `[ ]`. The integration has never been exercised against real Stripe.

## Proposed Solution

### 1. Webhook view hardening (`dashboard/booking/views.py`)
- Replace `except stripe.error.SignatureVerificationError` with `except stripe.SignatureVerificationError` to use the SDK's canonical (non-legacy) exception path. Apply the same change to `tests_stripe.py`. (Behavior is unchanged on the current pinned SDK; this is forward-compatibility hardening.)
- Add `authentication_classes = []` and decorate `dispatch` with `@method_decorator(csrf_exempt)` on `StripeWebhookView` to make the public, cookie-less webhook contract explicit.
- Add a `ProcessedStripeEvent` model storing the Stripe `event.id` (unique). At the start of `post()`, attempt `ProcessedStripeEvent.objects.create(event_id=event.id)`; on `IntegrityError` short-circuit with HTTP 200 (replay → no-op). Persist the row only after the booking update succeeds, inside a transaction.

### 2. Abandoned-booking cleanup
- **Add `created_at = models.DateTimeField(auto_now_add=True, db_index=True)` to the `Booking` model** and ship the corresponding migration. Field is currently absent; cleanup cannot work without it.
- Add a Django management command `cleanup_abandoned_bookings` that deletes bookings with `status='PENDING'` and `created_at` older than a configurable threshold (default 24h, env var `STRIPE_PENDING_BOOKING_TTL_HOURS`). Delete (rather than mark CANCELLED) — see `design.md` for rationale.
- Document running it via a system cron (recommended hourly). Do **not** introduce Celery or a new dependency for this — the project has none today.

### 3. Configuration & polish
- Update `dashboard/.env.example` with placeholders: `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `LANDING_URL`, `STRIPE_PENDING_BOOKING_TTL_HOURS`.
- In `stripe_utils.create_checkout_session`, replace the hard-coded product name with a value derived from `CompanyProfile.get_solo().name`, with a sensible fallback string if the profile is unset.

### 4. Documented E2E validation
- Add a `docs/stripe-e2e-checklist.md` describing the manual Stripe-CLI flow (forwarding webhooks, test card numbers, expected booking state transitions, GCal sync verification). Tasks reference this checklist.

## Impact

- **Capabilities affected:** `webhook` (security + idempotency), `payment-flow` (abandoned-booking lifecycle, multi-tenant product naming), `config` (env example completeness).
- **Database:** Two migrations — one to add `Booking.created_at` (verified missing), one for the new `ProcessedStripeEvent` model. The `Booking.created_at` migration uses `auto_now_add=True`, which backfills `NOW()` for existing rows; this is acceptable because the cleanup command only deletes rows older than the TTL and existing PRE-PAID PENDING rows (if any) will simply enjoy a fresh 24h window after deploy.
- **Operational:** A new cron entry is required in production. The cleanup command is idempotent and safe to run repeatedly.
- **Backwards compatibility:** All changes are additive or bug fixes; no API contract changes for the booking or landing apps.
- **Out of scope:** Frontend (`booking/`, `landing/`) — no changes required. Migration to `payment_intent.succeeded` event type — kept as a future change since current `payment_method_types=['card']` makes `checkout.session.completed` reliable.
