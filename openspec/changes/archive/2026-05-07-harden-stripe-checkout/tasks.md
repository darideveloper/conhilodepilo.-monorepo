# Tasks: Harden Stripe Checkout

## Phase 1: Webhook Correctness & Security

- [x] **Confirm SDK exception path**: in the dashboard venv, run `python -c "import stripe; print(stripe.SignatureVerificationError)"` to confirm the canonical path resolves on the pinned SDK before refactoring.
- [x] **Modernize signature exception class** in `dashboard/booking/views.py:191`: replace `stripe.error.SignatureVerificationError` with `stripe.SignatureVerificationError` (canonical, non-legacy path).
- [x] **Update test mock** in `dashboard/booking/tests_stripe.py:137` to use `stripe.SignatureVerificationError`. The test must continue to pass — this is a rename, not a behavioral change.
- [x] **Make webhook auth posture explicit**:
    - [x] Set `authentication_classes = []` on `StripeWebhookView`.
    - [x] Decorate `StripeWebhookView.dispatch` with `@method_decorator(csrf_exempt, name='dispatch')`.
    - [x] Add a unit test that verifies a cookie-less, CSRF-tokenless POST is accepted (with valid signature) and a session-cookied POST is also accepted (no false negative).

## Phase 2: Webhook Idempotency

- [x] **Add `ProcessedStripeEvent` model** to `dashboard/booking/models.py` with `event_id` (CharField, unique, max_length=255), `processed_at` (auto_now_add), and a string `__repr__`.
- [x] **Generate migration**: `python manage.py makemigrations booking`.
- [x] **Wrap webhook handler in transaction**: in `StripeWebhookView.post`, after signature verification, attempt `ProcessedStripeEvent.objects.create(event_id=event.id)` inside `transaction.atomic()`; on `IntegrityError` return HTTP 200 immediately.
- [x] **Add idempotency tests** in `tests_stripe.py`:
    - [x] Posting the same event twice updates the booking exactly once.
    - [x] Second delivery returns 200 without raising.

## Phase 3: Abandoned Booking Cleanup

- [x] **Add `Booking.created_at`** to `dashboard/booking/models.py` as `created_at = models.DateTimeField(auto_now_add=True, db_index=True)`. (Verified missing in current model.)
- [x] **Generate migration**: `python manage.py makemigrations booking` — confirm the migration only adds `created_at` and uses `auto_now_add` (existing rows backfilled to `NOW()` on apply).
- [x] **Add setting** `STRIPE_PENDING_BOOKING_TTL_HOURS` (default 24) to `dashboard/project/settings.py`, sourced from env.
- [x] **Create the management package skeleton** (does not exist today): `dashboard/booking/management/__init__.py` and `dashboard/booking/management/commands/__init__.py`.
- [x] **Create management command** `dashboard/booking/management/commands/cleanup_abandoned_bookings.py` that:
    - [x] Deletes (or marks CANCELLED — pick one and document) `Booking` rows with `status='PENDING'` and `created_at < now() - TTL`.
    - [x] Logs how many were cleaned up; supports `--dry-run`.
- [x] **Tests** for the management command:
    - [x] Old PENDING booking is removed; recent PENDING is preserved.
    - [x] CONFIRMED/PAID/CANCELLED bookings are never touched regardless of age.
    - [x] `--dry-run` does not mutate the DB.
- [x] **Operational docs**: add a "Cron" section to `docs/stripe-e2e-checklist.md` (created in Phase 5) describing the recommended hourly cron entry.

## Phase 4: Configuration & White-Label Polish

- [x] **Update `dashboard/.env.example`** (currently contains only `ENV=dev`) to include placeholders for `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `LANDING_URL`, `STRIPE_PENDING_BOOKING_TTL_HOURS`.
- [x] **Mirror** the new variables into `dashboard/.env.dev.example` and `dashboard/.env.prod.example` (both files confirmed to exist) using values appropriate for each environment (test keys for dev, blank/placeholder for prod).
- [x] **Replace hard-coded product name** in `dashboard/utils/stripe_utils.py:create_checkout_session`: use `CompanyProfile.get_solo().name` (cached at the top of the function), falling back to `"Booking"` if blank.
- [x] **Test** `create_checkout_session` uses the company name (assert via mocked `Session.create` call kwargs).

## Phase 5: Validation & Documentation

- [x] **Run full test suite**: `python manage.py test booking` — all green.
- [x] **Add E2E checklist**: create `docs/stripe-e2e-checklist.md` with:
    - [x] Stripe CLI install + `stripe listen --forward-to localhost:8000/api/stripe/webhook/` instructions.
    - [x] Test cards table (success: `4242 4242 4242 4242`, decline, 3DS).
    - [x] Expected DB state transitions for PRE-PAID and POST-PAID flows.
    - [x] Verification step for Google Calendar sync after `PAID` transition.
    - [x] Verification step for cleanup command behavior on an abandoned session.
- [x] **Execute the E2E checklist once** end-to-end against Stripe test mode and record the result in the checklist file (or a sibling `stripe-e2e-results.md`).
- [x] **Validate proposal**: `openspec validate harden-stripe-checkout --strict`.
