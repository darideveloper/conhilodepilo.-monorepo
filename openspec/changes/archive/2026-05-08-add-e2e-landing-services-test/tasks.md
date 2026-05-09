## 1. Extend LandingPage POM

- [x] 1.1 Add `getServicesSection()` — returns `Locator` for `#servicios`
- [x] 1.2 Add `getCards()` — returns all `article` locators inside `#servicios`
- [x] 1.3 Add `getFirstCard()` — returns `Locator` for `#servicios article:first-child` (convenience shortcut for `getCards().first()`)
- [x] 1.4 Add `waitForHydration()` — waits for the first pill button inside `#servicios` to be visible and enabled, confirming the `CategoryShowcase` React island has hydrated
- [x] 1.5 Add `assertCardCount(expected: number)` — asserts `getCards()` has count `expected` (replaces and extends `assertServiceCardCount`)
- [x] 1.6 Add `assertCardImageVisible(card: Locator)` — asserts an `img` element is visible inside the card and its `src` is non-empty
- [x] 1.7 Add `assertCardImagePlaceholderAbsent(card: Locator)` — asserts the gray placeholder `div.bg-gray-100` is NOT visible
- [x] 1.8 Add `assertCardName(card: Locator, expectedName: string)` — asserts `h3` text equals `expectedName`
- [x] 1.9 Add `assertCardDescriptionNonEmpty(card: Locator)` — asserts the description element has non-empty `innerText`
- [x] 1.10 Add `getServiceButtons(card: Locator)` — returns all pill `button` locators inside the card's services area
- [x] 1.11 Add `assertServiceButtonCount(card: Locator, expected: number)` — counts pill buttons
- [x] 1.12 Add `assertFirstPillSelected(card: Locator)` — asserts first pill has the selected CSS class (`bg-brand-primary`) and others do not
- [x] 1.13 Add `clickServiceButton(card: Locator, index: number)` — clicks the nth pill (0-indexed)
- [x] 1.14 Add `assertPillSelected(card: Locator, index: number)` — asserts pill at `index` is selected, others are not
- [x] 1.15 Add `getPriceText(card: Locator)` — returns the text of the price element (`span.text-xl.font-bold`)
- [x] 1.16 Add `getDurationText(card: Locator)` — returns the text of the duration `small` element
- [x] 1.17 Add `clickReservar(card: Locator)` — clicks the "Reservar" button in the card's footer

## 2. Create the Spec File

- [x] 2.1 Create `e2e/tests/landing/services-data.spec.ts` and import `test`, `expect` from `../../fixtures/base.js`, `fetchServices` from `../../helpers/api.js`, and `LandingPage` from `../../pages/landing/LandingPage.js`
- [x] 2.2 Add a `beforeEach` (or top-level) block that calls `fetchServices(request)`, filters out the courses group using `process.env['PUBLIC_COURSES_GROUP_ID']`, and calls `test.skip()` if no categories remain
- [x] 2.3 Add test **"services section renders correct card count"**: call `landing.open()`, wait for hydration, then call `landing.assertCardCount(nonCourseCategories.length)`
- [x] 2.4 Add test **"first card renders dashboard image, name, and description"**: use the first category from the API response; call `assertCardImageVisible`, `assertCardImagePlaceholderAbsent`, `assertCardName`, and `assertCardDescriptionNonEmpty` on `getFirstCard()`
- [x] 2.5 Add test **"first card pill buttons match API service count and first is pre-selected"**: use `firstCategory.services.length`; call `assertServiceButtonCount` and `assertFirstPillSelected`
- [x] 2.6 Add test **"clicking second pill updates selection, price, and duration"**: skip with `test.skip()` when `firstCategory.services.length < 2`; click second pill; call `assertPillSelected(card, 1)`, then compare `getPriceText()` and `getDurationText()` with second service's values from the API
- [x] 2.7 Add test **"Reservar button navigates to /booking/{service.id}"**: call `clickReservar(getFirstCard())`; assert `page.url()` ends with `/booking/${firstService.id}`

## 3. Validation

- [x] 3.1 Run `openspec validate add-e2e-landing-services-test --strict` and resolve any errors
- [x] 3.2 Run `npx playwright test --project=landing` against locally-running services and confirm all 5 tests pass (or skip gracefully when no data is present)
