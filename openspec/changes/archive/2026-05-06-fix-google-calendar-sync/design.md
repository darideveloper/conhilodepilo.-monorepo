## Context

The Google Calendar integration has accumulated multiple correctness gaps that prevent the desired invariant: **every booking state-change must be reflected in the calendar within seconds**. The fixes touch three subsystems (the service-layer module, Django signals, the booking view + Stripe webhook) and require a new reconciliation entry point. This design records why each decision is made.

## Goals / Non-Goals

**Goals**
- Calendar reflects bookings 1:1 for create, edit (date/time/services), cancel, and delete.
- Survives Stripe webhook delays, transient Google API failures, and partial DB failures.
- No new infrastructure dependencies (no Celery, no Redis).

**Non-Goals**
- Two-way sync (calendar → booking).
- Sending invitations to clients (explicitly opted out by user).
- Cron scheduling of reconciliation (follow-up).

## Decisions

### D1. Sync trigger — explicit `transaction.on_commit` instead of signal side-effects
Currently sync only happens because the m2m_changed handler saves `end_time`, which re-enters `post_save`. This is fragile — any future optimization that elides the redundant save breaks calendar sync silently.

**Decision:** Make sync explicit. Both `CreateBookingView` and the m2m_changed handler schedule `sync_booking_to_google` via `transaction.on_commit`. The `post_save` handler still runs for admin-initiated edits but its responsibilities narrow: handle `update_fields` skipping, status transitions, and PENDING gating.

**Alternatives considered:**
- Keep current side-effect path → fragile, already failing.
- Listen exclusively on m2m_changed → misses `Booking.save()` edits that don't touch services (e.g., admin changes start_time only).

### D2. CANCELLED → patch with `[CANCELLED]` prefix (not delete)
User explicitly requested keeping cancelled bookings on the calendar as records. Implementation: idempotent prefix on `summary` (don't double-prefix if already present), and `Estado: Cancelado` already appears in description via `get_status_display()`.

### D3. Asynchrony — `transaction.on_commit` + retry, not Celery
User confirmed no new infra. `on_commit` defers to after-DB-commit (avoiding race where signal fires before commit), and the in-process retry loop (3 attempts, 1s/2s/4s) handles transient 5xx/network. Pros: zero new dependencies, persistent FAILURE state in DB lets the reconcile command serve as durable retry. Cons: still occupies the request thread for retries — acceptable because Stripe webhook timeout is 10s and worst-case retry is ~7s; sync API calls typically resolve in <1s.

### D4. Idempotency via `extendedProperties.private.booking_id` lookup before insert
A failed DB write after a successful Google insert can lead to duplicate events on retry. The Google Calendar API's `events.insert` does **not** deduplicate by `iCalUID` (only `events.import` does, and it requires an `organizer` payload that doesn't fit our use case).

**Decision:** Tag every event with `extendedProperties.private.booking_id = <pk>`. Before `events().insert`, the sync function calls `events().list(calendarId=..., privateExtendedProperty=f"booking_id={booking.pk}", showDeleted=False, maxResults=1)`. If an event is returned, the code switches to `events().patch(eventId=<found_id>)` and updates `booking.google_event_id` to the discovered id. This adds one round-trip on the recovery path only — the happy path still uses the `google_event_id` already on the booking.

`iCalUID = booking-<pk>@<HOST_DOMAIN>` is still set on the body for human/audit traceability and to support manual cross-referencing, but is not relied upon for dedupe.

**Alternatives considered:**
- `iCalUID`-only → does not dedupe `events.insert`; would silently allow duplicates.
- `events.import` → requires organizer field; semantically meant for cross-calendar imports, not native creation.
- Store insert intent in DB before API call → more invasive; chose lookup-before-insert instead.

### D5. Timezone — `settings.TIME_ZONE`
`CompanyProfile` does not store a timezone, and the project convention (per `openspec/project.md`) is `Europe/Madrid` in production via Django's `TIME_ZONE` setting. Continue reading `settings.TIME_ZONE`; no model change required. If multi-tenant TZ ever becomes a requirement, that's a separate change.

### D6. Error recording — structured for `HttpError`
`str(e)` on a `googleapiclient.errors.HttpError` produces a long, opaque string. Format as `"{status} {reason}: {detail}"` so admins can triage by status code. Other exceptions: `f"{type(e).__name__}: {e}"` truncated.

### D7. Delete idempotency — 404 and 410 are success
Calendar event already gone is the desired terminal state. No need to surface as error.

### D8. Reconciliation command, not a periodic task
Adding a Django management command keeps the change scoped and lets ops decide when to run it. A future PR can add cron.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Retry loop blocks the request thread up to 7s | Worst case still under Stripe's 10s timeout; if Google has a major outage, FAILURE state + reconcile command provide recovery |
| Multiple environments writing to the same calendar would collide on `extendedProperties.booking_id` (since pks overlap) | Document: each environment MUST use its own `GOOGLE_CALENDAR_ID`. Add a startup warning in `apps.py` if `DEBUG=True` and `GOOGLE_CALENDAR_ID` is set to a known production value (best-effort; not enforced) |
| Race: two concurrent saves both perform the lookup and both insert | Bounded by the booking lock under `transaction.on_commit` ordering; on_commit handlers run sequentially per request. Cross-request race remains theoretically possible — relies on Google to surface the duplicate, which would then be cleaned up by the reconcile command |
| `transaction.on_commit` doesn't fire if outer transaction rolls back | This is desired behavior — booking didn't actually persist, so calendar event shouldn't either |
| Adding `Booking.updated_at` may break existing fixtures/tests using exact equality | Use `auto_now=True` and update fixtures only where comparing timestamps |
| Removing the `created=True` skip path may double-fire sync (post_save + m2m_changed) on initial creation, or (Booking.save() recomputing end_time) + m2m_changed on `start_time` edits | Add `"end_time"` to the post_save skip-set so the m2m handler's `save(update_fields=["end_time"])` and the `Booking.save()` end_time recomputation do NOT re-enter the sync path. The m2m_changed handler is the sole sync trigger when services or end_time change. Explicit `transaction.on_commit` from `CreateBookingView` is the sync trigger for new bookings. `post_save` only schedules sync for *other* saves (e.g., admin status changes, Stripe webhook). |

## Migration Plan

1. Land DB migration first (adds `Booking.updated_at`).
2. Deploy code; on startup, all existing bookings have `updated_at = NULL`.
3. Backfill `updated_at = start_time` (or current time) via data migration so reconcile command's drift query (`last_synced_at < updated_at`) works correctly.
4. Run reconcile once manually in staging to verify no false-positive drift.
5. Monitor `google_sync_status="FAILURE"` count for 24h.

**Rollback:** Revert code; the new fields are nullable and harmless if unused.

## Open Questions

(All resolved during planning — see proposal "Resolved decisions".)
