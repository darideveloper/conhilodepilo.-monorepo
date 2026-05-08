import type { Page } from '@playwright/test';
import { expect } from '@playwright/test';

// Page Object for the post-submission success state rendered inside BookingForm.
export class BookingSuccessPage {
  constructor(private readonly page: Page) {}

  async assertVisible(): Promise<void> {
    await expect(
      this.page.getByRole('heading', { name: /confirmad|confirmed|gracias|thank/i }),
    ).toBeVisible({ timeout: 15_000 });
  }

  async getSummaryText(): Promise<string> {
    const card = this.page.locator('[class*="Card"]').last();
    return card.innerText();
  }
}
