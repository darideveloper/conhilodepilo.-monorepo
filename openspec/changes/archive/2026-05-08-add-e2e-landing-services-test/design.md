# Design: E2E Test — Landing Services Section

## Context

The landing page renders the `CategoryShowcase` component using data fetched at Astro SSG time via `getServiceCategories()`, which calls `GET /api/services/` and filters out the courses group. The `CategoryShowcase` is a React island loaded with `client:load`, meaning the static HTML is present in the initial page response but React must hydrate before interactive elements (pill buttons) become clickable.

Each `CategoryCard` displays:
- A category-level image, name, and description sourced from `EventType` on the dashboard.
- A set of pill buttons (one per `Event` in the category), with the first pre-selected via React `useState`.
- The selected service's `price` and `duration` in the card footer, both sourced from the `Event`.
- A "Reservar" CTA that navigates to `/booking/{service.id}` via `window.location.href`.

The `e2e/helpers/api.ts` module already provides `fetchServices(request)`, which returns `ServiceCategory[]` and matches the landing's API contract exactly. Tests will use this helper to fetch the expected data and validate the rendered HTML against it.

## Goals / Non-Goals

- **Goals:**
  - Validate that at least one `CategoryCard` renders with dashboard-sourced data (image, name, description).
  - Validate that service pill buttons reflect the correct number and selection state from the API.
  - Validate the price/duration rendering and that pill clicks update them.
  - Validate the "Reservar" CTA navigates to the correct URL.
  - Skip gracefully if no services are configured in the dashboard.

- **Non-Goals:**
  - Testing the `CoursesSection` or `Gallery` — out of scope for this change.
  - Visual regression or pixel-level snapshot testing.
  - Testing all cards; the first card provides sufficient coverage of the rendering logic.

## Decisions

### Decision: Use `fetchServices()` to derive expected values
Rather than hard-coding service names or prices in the test, use `fetchServices(request)` (from `e2e/helpers/api.ts`) to fetch the live API response and build assertions from it. This makes the tests data-independent and resilient to dashboard content changes.

**Alternatives considered:**
- Hard-coded fixtures — brittle; any dashboard change breaks the test.
- Environment variable for expected count — partially useful but does not validate field values.

### Decision: Extend `LandingPage` POM rather than create a separate `CategoryCardPage`
`CategoryCard` elements are always children of `#servicios article`. Scoping a `Locator` from `LandingPage` keeps the POM graph flat and avoids a separate class for what is essentially an assertion scope. New methods accept a `card: Locator` parameter so they can be applied to any card, not just the first.

**Alternatives considered:**
- Separate `CategoryCardPage` POM class — unnecessary indirection for a list of homogeneous items.

### Decision: Wait for React hydration before interactive assertions
The `CategoryShowcase` uses `client:load`. Static HTML is present immediately, but pill click handlers are not attached until React hydrates. The test MUST wait for the first pill button inside `#servicios` to become clickable (using `waitForSelector` with state `'attached'` or waiting for the locator's `isEnabled()` to resolve) before executing click-based assertions.

### Decision: `courses` group filtering at test level
The test must filter `fetchServices()` output to exclude the `courses` group before computing the expected card count — exactly as `getServiceCategories()` does using `PUBLIC_COURSES_GROUP_ID`. The env var `PUBLIC_COURSES_GROUP_ID` is already available in the landing project's environment; in E2E, the test can read it via `process.env['PUBLIC_COURSES_GROUP_ID']` or simply count cards returned by the `#servicios` selector and verify they are ≥ 1. The simplest correct approach is to call `fetchServices()` (which returns all categories including courses), apply the same `group_id` filter, and compare.

## Risks / Trade-offs

- **Risk: Dashboard has no services configured in CI** → Mitigated by a `test.skip()` guard matching the pattern established in `e2e-testing` spec.
- **Risk: First category has only one service** → The pill-click test for price/duration update is conditionally skipped when the category has fewer than two services. A comment in the spec documents this skip condition.
- **Risk: Image assertion coupling** → The `img[src]` check verifies the path contains `/media/` or the dashboard host. If the dashboard migrates to S3, the path changes. Mitigated by checking `img[src]` is non-empty and not a placeholder, rather than asserting an exact host prefix.

## Open Questions

None. All design decisions are resolved above.
