import { test, expect } from '../../fixtures/base.js';
import { BookingFlowPage } from '../../pages/booking/BookingFlowPage.js';

// Example spec: proves the booking harness boots and can load the wizard.
// Not a full booking-flow test — concrete coverage is added in follow-on work.

test('booking wizard renders Step 1 on load', async ({ page }) => {
  const flow = new BookingFlowPage(page);
  await flow.open();

  // The Card component wrapping Step 1 must be visible after hydration
  await flow.assertStep1Visible();

  // Page title should be non-empty (SSR meta from Astro)
  await expect(page).toHaveTitle(/.+/);
});
