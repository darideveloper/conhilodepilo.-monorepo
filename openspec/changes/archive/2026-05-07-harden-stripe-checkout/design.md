# Design: Harden Stripe Checkout

## Why a design doc
Three of the seven fixes touch behavior across the webhook lifecycle (exception handling, CSRF posture, idempotency) and one introduces a new background process (cleanup command). Documenting the trade-offs prevents the apply stage from re-litigating choices.

## 1. Signature exception class
The Stripe Python SDK exposes exceptions both at the top level (`stripe.SignatureVerificationError`) and under the legacy `stripe.error.*` namespace. On the currently pinned SDK (`stripe>=11.4.0`, installed 15.1.0) the legacy alias is still present and resolves to the same class object — so the existing code is **not** broken at runtime today. The change is forward-compatibility hardening: Stripe's docs and examples now use the top-level path, and the legacy alias is a candidate for removal in a future major version. The rename is mechanical and behavior is identical on the current SDK.

This was originally flagged as a runtime bug in the audit — that was incorrect. Reframed here as modernization, not a fix.

## 2. CSRF / authentication posture
DRF's `SessionAuthentication` enforces CSRF only when the request carries a session cookie. Stripe's webhooks don't, so the current setup works — incidentally. The hardening:
- `authentication_classes = []` — webhooks have no Django identity; declaring this prevents accidental session-bound CSRF enforcement if defaults change.
- `@method_decorator(csrf_exempt, name='dispatch')` — defense in depth against future middleware additions or a `CsrfViewMiddleware` reorder.

This pair is the canonical Django/DRF idiom for service-to-service POST endpoints.

## 3. Webhook idempotency
**Decision:** track event IDs in a small Django model rather than relying on `booking.status` checks.

Alternatives considered:
- *Cache-based dedupe (Redis)*: rejected — the project has no Redis dependency and adding one for a low-volume webhook is over-engineering.
- *Status-guard only*: rejected — incidental, breaks the moment any other event type is wired up (e.g. `payment_intent.succeeded`).
- *Stripe's idempotency keys on outbound calls*: orthogonal — those protect outbound `Session.create` retries, not inbound webhook redelivery.

**Schema:**
```
ProcessedStripeEvent
  event_id    CharField(max_length=255, unique=True)
  processed_at DateTimeField(auto_now_add=True)
```

**Flow:**
```
post() → verify signature → transaction.atomic():
    try ProcessedStripeEvent.objects.create(event_id=event.id)
    except IntegrityError: return 200 (replay)
    handle event
```

Creating the row first (rather than after) closes the race where two concurrent deliveries both pass the "not yet processed" check. `unique=True` is the actual lock.

**Retention:** unbounded growth is fine for the next several years at this volume. If it ever matters, the cleanup command in Phase 3 can be extended to drop rows older than 30 days.

## 4. Abandoned booking cleanup
**Decision:** management command + system cron.

Alternatives considered:
- *Celery beat / RQ scheduler*: rejected — no existing async infra; introduces a new operational surface.
- *Django signals on Stripe `checkout.session.expired` event*: viable, but requires subscribing to a second event type and handles only sessions Stripe knows expired. Misses the case where session creation succeeded but the user closes the tab and the dashboard restarts before the expiry event fires. Also doesn't address the "session creation crashed mid-flight" case.
- *On-demand cleanup at booking creation time*: rejected — couples cleanup latency to user traffic; a slot held by a stale booking remains blocked until the next booking attempt for that slot.

The cron approach is the simplest correct solution: it runs hourly regardless of traffic, and `--dry-run` makes it safe to introspect.

**Delete vs. mark CANCELLED:** delete. Reasons:
- The `Booking` row never represented a real commitment (no payment received).
- Keeping it as `CANCELLED` clutters the admin and complicates availability queries.
- Audit trail is preserved by the Stripe Checkout Session record on Stripe's side.

If the team later wants an audit row, switching to `CANCELLED` is a one-line change.

**TTL default:** 24 hours, matching Stripe's default Checkout Session expiry. Configurable via `STRIPE_PENDING_BOOKING_TTL_HOURS` so test environments can shorten it.

**Schema prerequisite:** `Booking` has no `created_at` column today. The migration adds it with `auto_now_add=True`, which writes `NOW()` for every existing row. Implication: any pre-existing PRE-PAID `PENDING` bookings that were already abandoned before this deploy will get a fresh 24-hour grace period rather than being cleaned up immediately. This is acceptable — the alternative (manually backfilling timestamps from `start_time` or wiping pending rows on deploy) introduces more risk than it saves. Add `db_index=True` because the cleanup query filters on `created_at`.

## 5. Product name from CompanyProfile
`CompanyProfile` is a `django-solo` singleton, so `get_solo()` is cheap and safe. The fallback (`"Booking"`) is for the edge case of a fresh database where the singleton has not been customized. No localization concern at the Stripe layer — the user sees the Stripe Checkout page in their own locale; product name is descriptive metadata.

## What this proposal does NOT do
- Migrate from `checkout.session.completed` to `payment_intent.succeeded`. With `payment_method_types=['card']`, the existing event is reliable and synchronous. Revisit when adding async payment methods (SEPA, ACH).
- Add Stripe Tax, coupons, or multi-line items. Out of scope.
- Change the frontend redirect logic or success/cancel pages.
- Replace the Stripe SDK pinning. `>=11.4.0` is current.
