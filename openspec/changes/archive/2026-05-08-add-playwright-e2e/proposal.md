# Change: Add Playwright E2E Testing Architecture

## Why

The monorepo has no cross-service end-to-end testing layer. Dashboard behavior (bookings, integrations, admin flows), user booking workflows, and Stripe/Google Calendar integrations can only be validated manually today. A dedicated Playwright project adds a reliable, repeatable harness for those journeys without coupling to any single service's unit-test setup.

## What Changes

- **New top-level project** `e2e/` — a standalone Playwright + TypeScript package inside the monorepo. This is intentionally separate from `dashboard/`, `landing/`, and `booking/` so that test-only dependencies never leak into production builds.
- **Page Object Model (POM) layer** (`e2e/pages/`) — one class per major UI surface (booking flow, dashboard admin, landing). POMs are the only place that knows CSS selectors, so tests stay readable and resilient to markup changes.
- **Fixture layer** (`e2e/fixtures/`) — `auth.ts` provides `adminCredentials` (read from `DASHBOARD_ADMIN_USER`/`DASHBOARD_ADMIN_PASS` env vars); `base.ts` re-exports it as the single `test` export for all specs. No programmatic seed fixture exists — the Dashboard exposes no write APIs for most models; test data for non-booking entities must be created via the admin UI.
- **Helper utilities** (`e2e/helpers/`) — typed wrappers around the Dashboard REST API using Playwright's `APIRequestContext` (which inherits `ignoreHTTPSErrors: true`). Provides `createBooking`, `fetchServices`, `fetchAvailableSlots`.
- **Test directories** (`e2e/tests/`) — organised by workflow domain: `booking/`, `dashboard/`, `integrations/`. Each domain gets its own sub-folder; files are `*.spec.ts`.
- **One example spec per domain** — demonstrates the pattern without testing any real feature in full. Concrete coverage is added incrementally after the architecture is approved.
- **Environment config** (`e2e/.env.example`, `playwright.config.ts`) — maps to the portless dev-server domains (`*.conhilodepilo.localhost`) via `BOOKING_URL`, `DASHBOARD_URL`, `LANDING_URL`, `DASHBOARD_ADMIN_USER`, `DASHBOARD_ADMIN_PASS`.
- **Dev orchestration update** — `dev.sh` gains a note (and an optional tmux window) for running the E2E suite; no existing windows are removed or modified.

## Implementation Notes

- **Spanish admin UI** — the Django admin is fully translated to Spanish (Django Unfold). All dashboard selectors use stable Django input IDs (`#id_username`, `#id_password`) and Spanish button text (`Iniciar sesión`) rather than English label text.
- **Login redirect** — `LoginPage.open()` navigates to `/admin/` (not `/admin/login/`) so Django sets `?next=/admin/` automatically; without this, successful login redirects to `/accounts/profile/`.
- **shadcn `Card` selector** — the `Card` component renders `data-slot="card"` on its root element; class names are Tailwind utilities only. Selector is `[data-slot="card"]`.
- **Booking list assertion** — `client_email` is only in `search_fields`, not `list_display`. Assertions use `client_name` (which is in `list_display`) with a unique timestamp per run.
- **Node.js TLS** — `ignoreHTTPSErrors: true` only applies to the Playwright browser context. All `helpers/api.ts` functions use `APIRequestContext` (the Playwright `request` fixture) so they inherit the same TLS bypass.
- **No `deleteBooking`** — the Dashboard exposes no `DELETE /api/bookings/:id` endpoint. Test records created by the integration example accumulate in the dev DB; this is acceptable for local development.

## Impact

- Affected specs: *(new)* `e2e-testing`
- Affected code:
  - New: `e2e/` (entire project)
  - Minor update: `dev.sh` (documentation comment, optional tmux window)
  - No changes to `dashboard/`, `booking/`, or `landing/` source files
- No breaking changes to existing behaviour
