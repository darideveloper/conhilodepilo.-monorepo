import type { Locator, Page } from '@playwright/test';
import { expect } from '@playwright/test';

// Page Object for the Con Hilo Depilo marketing landing page.
export class LandingPage {
  constructor(private readonly page: Page) {}

  async open(): Promise<void> {
    // domcontentloaded avoids waiting for the Google Maps iframe in the footer,
    // which is unreachable in local/CI environments and causes load to hang.
    await this.page.goto('/', { waitUntil: 'domcontentloaded' });
  }

  async assertHeroVisible(): Promise<void> {
    // The hero section has id="hero" in HeroSection.astro
    await expect(this.page.locator('#hero')).toBeVisible({ timeout: 10_000 });
  }

  // ── Services section ──────────────────────────────────────────────────────

  getServicesSection(): Locator {
    return this.page.locator('#servicios');
  }

  // Returns all CategoryCard article elements inside #servicios.
  getCards(): Locator {
    return this.page.locator('#servicios article');
  }

  getFirstCard(): Locator {
    return this.getCards().first();
  }

  // Waits until the first service pill button is visible and enabled, confirming
  // the CategoryShowcase React island (client:load) has fully hydrated.
  async waitForHydration(): Promise<void> {
    await expect(
      this.page.locator('#servicios article button').first(),
    ).toBeEnabled({ timeout: 15_000 });
  }

  async assertCardCount(expected: number): Promise<void> {
    await expect(this.getCards()).toHaveCount(expected, { timeout: 10_000 });
  }

  // Kept for backward compatibility — delegates to assertCardCount.
  async assertServiceCardCount(expectedCount: number): Promise<void> {
    await this.assertCardCount(expectedCount);
  }

  // ── Card image ────────────────────────────────────────────────────────────

  async assertCardImageVisible(card: Locator): Promise<void> {
    const img = card.locator('img').first();
    await expect(img).toBeVisible({ timeout: 10_000 });
    const src = await img.getAttribute('src');
    expect(src).toBeTruthy();
  }

  // The gray bg-gray-100 placeholder is only rendered when category.image is null.
  async assertCardImagePlaceholderAbsent(card: Locator): Promise<void> {
    await expect(card.locator('.bg-gray-100')).not.toBeVisible();
  }

  // ── Card text ─────────────────────────────────────────────────────────────

  async assertCardName(card: Locator, expectedName: string): Promise<void> {
    await expect(card.locator('h3')).toHaveText(expectedName, { timeout: 10_000 });
  }

  // The description is rendered via dangerouslySetInnerHTML with .prose classes.
  async assertCardDescriptionNonEmpty(card: Locator): Promise<void> {
    const description = card.locator('.prose').first();
    const text = await description.innerText();
    expect(text.trim().length).toBeGreaterThan(0);
  }

  // ── Pill buttons ──────────────────────────────────────────────────────────

  // Returns buttons in the "Servicios disponibles" group only (excludes "Reservar").
  getServiceButtons(card: Locator): Locator {
    return card.locator('button').filter({ hasNotText: 'Reservar' });
  }

  async assertServiceButtonCount(card: Locator, expected: number): Promise<void> {
    await expect(this.getServiceButtons(card)).toHaveCount(expected, { timeout: 10_000 });
  }

  // Selected pill has bg-brand-primary class; unselected pills use bg-ui-bg-light.
  async assertFirstPillSelected(card: Locator): Promise<void> {
    await expect(this.getServiceButtons(card).first()).toHaveClass(
      /bg-brand-primary/,
      { timeout: 10_000 },
    );
  }

  async clickServiceButton(card: Locator, index: number): Promise<void> {
    await this.getServiceButtons(card).nth(index).click();
  }

  async assertPillSelected(card: Locator, index: number): Promise<void> {
    const pills = this.getServiceButtons(card);
    const count = await pills.count();
    await expect(pills.nth(index)).toHaveClass(/bg-brand-primary/, { timeout: 10_000 });
    for (let i = 0; i < count; i++) {
      if (i !== index) {
        await expect(pills.nth(i)).not.toHaveClass(/bg-brand-primary/);
      }
    }
  }

  // ── Footer: price & duration ──────────────────────────────────────────────

  async getPriceText(card: Locator): Promise<string> {
    // CategoryCard renders the price as <span className="text-xl font-bold text-ui-text-main">
    return card.locator('span.text-xl').first().innerText();
  }

  async getDurationText(card: Locator): Promise<string> {
    // CategoryCard renders duration inside the only <small> element in the card footer.
    return card.locator('small').innerText();
  }

  // ── Reservar CTA ──────────────────────────────────────────────────────────

  async clickReservar(card: Locator): Promise<void> {
    await card.getByRole('button', { name: /Reservar/i }).click();
  }
}
