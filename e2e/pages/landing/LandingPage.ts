import type { Page } from '@playwright/test';
import { expect } from '@playwright/test';

// Page Object for the Con Hilo Depilo marketing landing page.
export class LandingPage {
  constructor(private readonly page: Page) {}

  async open(): Promise<void> {
    await this.page.goto('/');
  }

  async assertHeroVisible(): Promise<void> {
    // The hero section has id="hero" in HeroSection.astro
    await expect(this.page.locator('#hero')).toBeVisible({ timeout: 10_000 });
  }

  async assertServiceCardCount(expectedCount: number): Promise<void> {
    // CategoryShowcase renders service cards; use section id="servicios" as scope
    const section = this.page.locator('#servicios');
    const cards = section.locator('[class*="card"], [class*="Card"]');
    await expect(cards).toHaveCount(expectedCount, { timeout: 10_000 });
  }
}
