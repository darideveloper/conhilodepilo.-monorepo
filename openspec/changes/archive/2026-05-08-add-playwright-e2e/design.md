# Design: Playwright E2E Architecture

## Context

The monorepo currently tests each service in isolation:
- **Dashboard** — Django `TestCase` / `APIClient` (SQLite in-memory, mocked Google + Stripe).
- **Landing** — Vitest unit tests.
- **Booking** — no automated tests at all.

There is no layer that crosses service boundaries or drives a real browser. The goal is to add one, keeping it a zero-friction addition to the existing setup.

## Goals / Non-Goals

**Goals**
- Standalone Playwright project that any developer can `npm install && npx playwright test` without touching any service.
- Page Object Model so selectors are centralised, not scattered across test files.
- Work against locally-running dev services (same URLs as `dev.sh`).
- Single example spec per domain to prove the harness compiles and runs.

**Non-Goals**
- Full workflow coverage (that is follow-on work).
- CI/CD pipeline changes (can be added later as a separate change).
- Mocking or stubbing the Dashboard API within E2E tests (tests hit a real dev/test server).
- Replacing existing Django unit tests.
- Programmatic seed/teardown fixtures — the Dashboard exposes no write APIs for most models.

---

## Directory Layout

```
e2e/
├── package.json               # @playwright/test, typescript, dotenv, date-fns, @types/node
├── tsconfig.json              # strict, module: NodeNext
├── playwright.config.ts       # projects: booking | dashboard | landing | integrations
├── .env.example               # BOOKING_URL, DASHBOARD_URL, LANDING_URL,
│                              # DASHBOARD_ADMIN_USER, DASHBOARD_ADMIN_PASS
│
├── fixtures/
│   ├── base.ts                # re-exports auth as the single `test` export
│   └── auth.ts                # adminCredentials fixture (env vars → admin/admin default)
│
├── pages/
│   ├── booking/
│   │   ├── BookingFlowPage.ts       # service selection → date → time → form → confirm
│   │   └── BookingSuccessPage.ts    # post-submit success / cancel screens
│   ├── dashboard/
│   │   ├── LoginPage.ts             # /admin login form (Spanish UI, stable Django IDs)
│   │   └── BookingListPage.ts       # /admin booking change-list
│   └── landing/
│       └── LandingPage.ts           # home page hero + service cards
│
├── helpers/
│   ├── api.ts                 # APIRequestContext wrappers: createBooking,
│   │                          # fetchServices, fetchAvailableSlots
│   └── dates.ts               # date formatting helpers (toApiDate, toApiTime, daysFromNow)
│
└── tests/
    ├── booking/
    │   └── booking-flow.example.spec.ts
    ├── dashboard/
    │   └── admin-login.example.spec.ts
    └── integrations/
        └── booking-to-dashboard.example.spec.ts
```

---

## Decisions

### Decision: Standalone project at `e2e/`
**Why:** Playwright and its browser binaries (~300 MB) must never appear in `booking/node_modules` or `landing/node_modules`. A separate `package.json` isolates the dependency graph and allows CI to install only what it needs for E2E runs.
**Alternative considered:** Adding Playwright to `booking/` as a dev dependency. Rejected — bloats the frontend build environment and couples test tooling to an application service.

### Decision: Playwright over Selenium
**Why:** Project already uses Stagehand (which wraps Playwright internally). Playwright provides a built-in TypeScript runner, trace viewer, network interception, and parallel workers with no external grid.
**Alternative considered:** Keeping Selenium (referenced in `project.md`). Rejected — `project.md` only mentions it as a possibility, no Selenium tests actually exist.

### Decision: Page Object Model (POM)
**Why:** Isolates selectors from test logic. When the booking wizard gains a new step, only `BookingFlowPage.ts` needs updating — all specs calling `flow.selectService()` pick up the fix automatically.
**Alternative considered:** Bare `page.locator()` calls in spec files. Rejected — creates selector sprawl and makes refactors expensive.

### Decision: No seed fixture — `createBooking` called directly in tests
**Why:** The Dashboard exposes no write APIs for most models (services, availability, company config). Only `POST /api/bookings/` exists as a public write endpoint. A general seed fixture implied CRUD capabilities that don't exist, and the `deleteBooking` placeholder would silently fail cleanup on every run. Calling `createBooking(request, payload)` directly in the integration spec is simpler and honest about what the API actually supports.
**Alternative considered:** Keeping `seed.ts` with a no-op teardown. Rejected — dead code that misleads future contributors about available API capabilities.

### Decision: `APIRequestContext` for all helper API calls
**Why:** Node.js built-in `fetch()` validates TLS certificates and rejects the self-signed certs used by portless. `ignoreHTTPSErrors: true` in `playwright.config.ts` only applies to the browser context. Playwright's `request` fixture (an `APIRequestContext`) inherits that setting and handles HTTPS correctly with no per-call workarounds.
**Alternative considered:** `NODE_TLS_REJECT_UNAUTHORIZED=0`. Rejected — disables TLS validation globally for the entire Node.js process, which is too broad.

### Decision: Stable Django input IDs for dashboard selectors
**Why:** The Django admin UI is fully translated to Spanish (via Django Unfold + locale). Label text (`Nombre de usuario`, `Contraseña`, `Iniciar sesión`) would require all selectors to be in Spanish, which is brittle if translations change. Django always renders `id="id_<fieldname>"` on form inputs regardless of locale — these are stable identifiers.
**Alternative considered:** `getByLabel(/username/i)`. Rejected — fails because the rendered label is `Nombre de usuario`.

### Decision: Navigate to `/admin/` for login, not `/admin/login/`
**Why:** Navigating directly to `/admin/login/` has no `next` parameter. After a successful login, Django falls back to `LOGIN_REDIRECT_URL` which defaults to `/accounts/profile/`. Navigating to `/admin/` triggers Django's redirect to `/admin/login/?next=/admin/`, ensuring the post-login destination is always the admin dashboard.

### Decision: Assert booking list row by `client_name`, not `client_email`
**Why:** The Booking admin's `list_display` is `("client_name", "start_time", "end_time", "status", …)`. The `client_email` field is only in `search_fields` and is never rendered in the table row HTML. Filtering rows by email always returns no matches.
**Alternative considered:** Using the admin search bar to filter by email before asserting. Rejected — adds unnecessary steps to the example spec.

### Decision: `.env` for base URLs and admin credentials
**Why:** The same spec files run against local dev and against other environments by changing a single `.env` file. No hardcoded URLs or credentials in test code.

---

## Playwright Config (`playwright.config.ts`)

```typescript
import { defineConfig, devices } from '@playwright/test';
import * as dotenv from 'dotenv';
dotenv.config();

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: process.env['CI'] ? 2 : 0,
  reporter: [['html', { open: 'never' }], ['list']],
  use: {
    ignoreHTTPSErrors: true,   // portless serves HTTPS with self-signed/invalid certs locally
    trace: 'on-first-retry',
    video: 'on-first-retry',
  },
  projects: [
    { name: 'booking',      testMatch: 'tests/booking/**/*.spec.ts',      use: { ...devices['Desktop Chrome'], baseURL: process.env['BOOKING_URL']   ?? 'https://booking.conhilodepilo'   } },
    { name: 'dashboard',    testMatch: 'tests/dashboard/**/*.spec.ts',    use: { ...devices['Desktop Chrome'], baseURL: process.env['DASHBOARD_URL'] ?? 'https://dashboard.conhilodepilo' } },
    { name: 'landing',      testMatch: 'tests/landing/**/*.spec.ts',      use: { ...devices['Desktop Chrome'], baseURL: process.env['LANDING_URL']   ?? 'https://landing.conhilodepilo'   } },
    { name: 'integrations', testMatch: 'tests/integrations/**/*.spec.ts', use: { ...devices['Desktop Chrome'], baseURL: process.env['DASHBOARD_URL'] ?? 'https://dashboard.conhilodepilo' } },
  ],
});
```

---

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Tests flake when dev server is not running | `playwright.config.ts` can add `webServer` entries to auto-start services; documented as follow-on work |
| E2E suite slow if run against all browsers | Default project targets Chrome only; WebKit / Firefox opt-in via `--project` flag |
| No booking cleanup after integration test | Test records accumulate in dev DB; acceptable locally. A `DELETE /api/bookings/:id` endpoint would enable cleanup |
| Dashboard selectors break on Unfold upgrade | Unfold uses `id="result_list"`, `id="id_<field>"` — these are Django conventions, not Unfold-specific, so they are stable |

---

## Migration Plan

No existing code was modified. The `e2e/` project is fully additive. Subsequent stages can:
1. Add `webServer` entries to `playwright.config.ts` to start dev servers automatically.
2. Add a GitHub Actions workflow that runs `npx playwright test`.
3. Expand POM classes and test coverage one workflow at a time.
