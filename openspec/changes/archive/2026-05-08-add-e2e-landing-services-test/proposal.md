# Change: Add E2E Test — Landing Services Section Renders Dashboard Data

## Why
The landing page fetches service categories from the dashboard API (`GET /api/services/`) at Astro build/request time and renders a `CategoryShowcase` grid from that data. There are currently no E2E tests validating that this integration works correctly end-to-end. A broken API call, a missing image, or a serialization regression would silently produce an empty or broken services grid — the most prominent section of the landing page. This change adds the first real-content landing test to the Playwright suite.

## What Changes
- New E2E spec file `e2e/tests/landing/services-data.spec.ts` with five focused test cases covering the full service card rendering path.
- Extended `LandingPage` POM (`e2e/pages/landing/LandingPage.ts`) with assertion and action methods scoped to `CategoryCard` elements inside `#servicios`.
- New OpenSpec capability `e2e-landing-services` documenting the test requirements and scenarios.

## Impact
- Affected specs: `e2e-landing-services` (new capability)
- Unaffected specs: `e2e-testing` (architectural harness requirements already captured and do not change)
- Affected code: `e2e/pages/landing/LandingPage.ts` (extended), `e2e/tests/landing/` (new spec file added)
- No changes to `dashboard/`, `landing/`, or `booking/` source code
