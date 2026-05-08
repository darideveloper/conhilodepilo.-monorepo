import type { Page, Locator } from '@playwright/test';
import { expect } from '@playwright/test';

// Page Object for the Django admin booking change-list at /admin/booking/booking/.
export class BookingListPage {
  constructor(private readonly page: Page) {}

  async open(): Promise<void> {
    await this.page.goto('/admin/booking/booking/');
  }

  // Returns the table row that contains the given text (use client_name — it is
  // in list_display; client_email is only in search_fields and not rendered).
  findBookingRow(clientName: string): Locator {
    return this.page.locator('#result_list tbody tr').filter({ hasText: clientName });
  }

  async assertRowVisible(clientName: string): Promise<void> {
    await expect(this.findBookingRow(clientName)).toBeVisible({ timeout: 10_000 });
  }
}
