## 1. Scaffold `e2e/` project

- [x] 1.1 Create `e2e/package.json` with `@playwright/test`, `typescript`, `dotenv`, `date-fns`, `@types/node` as dev dependencies
- [x] 1.2 Create `e2e/tsconfig.json` (strict, `moduleResolution: NodeNext`)
- [x] 1.3 Create `e2e/.env.example` with `BOOKING_URL`, `DASHBOARD_URL`, `LANDING_URL`, `DASHBOARD_ADMIN_USER`, `DASHBOARD_ADMIN_PASS`
- [x] 1.4 Root `.gitignore` line 8 already has bare `.env` pattern — covers `e2e/.env` at any depth; no change needed

## 2. Playwright configuration

- [x] 2.1 Create `e2e/playwright.config.ts` with four named projects: `booking`, `dashboard`, `landing`, `integrations`
- [x] 2.2 Configure each project's `baseURL` from env var; defaults match portless `.localhost` domains
- [x] 2.3 Set `ignoreHTTPSErrors: true`, `trace: 'on-first-retry'`, `video: 'on-first-retry'` in global `use`
- [x] 2.4 Configure HTML reporter (`open: 'never'`) + list reporter

## 3. Fixture layer (`e2e/fixtures/`)

- [x] 3.1 Create `e2e/fixtures/auth.ts` — `adminCredentials` fixture: reads `DASHBOARD_ADMIN_USER`/`DASHBOARD_ADMIN_PASS`, defaults to `admin`/`admin`
- [x] 3.2 ~~`seed.ts`~~ — **not created**; the Dashboard has no write APIs for most models; data must be created via the admin UI. No programmatic seed/teardown fixture exists.
- [x] 3.3 Create `e2e/fixtures/base.ts` — re-exports `auth` as the single `test` export; re-exports `expect`

## 4. Helper utilities (`e2e/helpers/`)

- [x] 4.1 Create `e2e/helpers/api.ts` — `APIRequestContext` wrappers (not bare `fetch`): `createBooking`, `fetchServices`, `fetchAvailableSlots`. No `deleteBooking` — no DELETE endpoint exists on the Dashboard.
- [x] 4.2 Create `e2e/helpers/dates.ts` — `toApiDate`, `toApiTime`, `daysFromNow` (wraps `date-fns`)

## 5. Page Object Model (`e2e/pages/`)

- [x] 5.1 Create `e2e/pages/booking/BookingFlowPage.ts` — `assertStep1Visible()` uses `[data-slot="card"]` (shadcn `Card` has no class containing "Card", only `data-slot`)
- [x] 5.2 Create `e2e/pages/booking/BookingSuccessPage.ts` — `assertVisible()`, `getSummaryText()`
- [x] 5.3 Create `e2e/pages/dashboard/LoginPage.ts` — `open()` navigates to `/admin/` (not `/admin/login/`) to get proper `?next=/admin/` redirect; uses `#id_username`, `#id_password` (stable Django IDs); button text is `Iniciar sesión` (Spanish UI)
- [x] 5.4 Create `e2e/pages/dashboard/BookingListPage.ts` — `findBookingRow(clientName)` / `assertRowVisible(clientName)` filter by `client_name` (in `list_display`); `client_email` is only in `search_fields` and never rendered in row HTML
- [x] 5.5 Create `e2e/pages/landing/LandingPage.ts` — `open()`, `assertHeroVisible()` (`#hero`), `assertServiceCardCount(n)`

## 6. Example specs (`e2e/tests/`)

- [x] 6.1 Create `e2e/tests/booking/booking-flow.example.spec.ts` — asserts `[data-slot="card"]` visible and page title non-empty
- [x] 6.2 Create `e2e/tests/dashboard/admin-login.example.spec.ts` — asserts `#login-form`, `#id_username`, `#id_password`, and `Iniciar sesión` button visible
- [x] 6.3 Create `e2e/tests/integrations/booking-to-dashboard.example.spec.ts` — calls `createBooking(request, …)` directly with a unique `clientName`; logs in via `LoginPage`; asserts row by `clientName` in `BookingListPage`; skips gracefully if no services/availability

## 7. Dev tooling updates

- [x] 7.1 `"test:e2e": "playwright test"` added to `e2e/package.json`
- [x] 7.2 `"test:e2e:ui": "playwright test --ui"` added
- [x] 7.3 `dev.sh` updated with comment block: first-time setup, per-project run commands, UI mode
- [x] 7.4 Optional tmux window for `e2e/` added to `dev.sh` as a commented-out line

## 8. Validation

- [x] 8.1 `openspec validate add-playwright-e2e --strict` passes clean
- [x] 8.2 `npm install` succeeded; `@types/node` required to resolve `process` type errors
- [x] 8.3 `npx tsc --noEmit` passes with zero errors
- [x] 8.4 `npx playwright test --list` discovers all 3 example specs across 3 projects
- [x] 8.5 All 3 tests pass against locally-running dev services
