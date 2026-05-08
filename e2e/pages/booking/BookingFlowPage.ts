import type { Page } from '@playwright/test';

export interface ContactFormData {
  fullName: string;
  email: string;
  phone?: string;
  specialRequests?: string;
}

// Page Object for the multi-step booking wizard.
// Steps: 1 = service selection, 2 = calendar, 3 = contact form.
export class BookingFlowPage {
  constructor(private readonly page: Page) {}

  async open(): Promise<void> {
    await this.page.goto('/');
  }

  async openWithService(serviceId: string): Promise<void> {
    await this.page.goto(`/?service=${serviceId}`);
  }

  // Step 1: select a service type and a service from the dropdowns, then continue.
  async selectService(serviceTypeId: string, serviceId: string): Promise<void> {
    const typeSelect = this.page.locator('select').first();
    await typeSelect.selectOption(serviceTypeId);

    const serviceSelect = this.page.locator('select').nth(1);
    await serviceSelect.selectOption(serviceId);

    await this.page.getByRole('button', { name: /añadir|add/i }).click();
    await this.page.getByRole('button', { name: /continuar|continue/i }).click();
  }

  // Step 2: click a day on the calendar then pick a time slot.
  async selectDate(dayLabel: string): Promise<void> {
    // The calendar renders days as buttons inside the react-day-picker
    await this.page.getByRole('button', { name: dayLabel, exact: true }).click();
  }

  async selectTime(slot: string): Promise<void> {
    await this.page.getByRole('button', { name: slot }).click();
    await this.page.getByRole('button', { name: /continuar|continue/i }).click();
  }

  // Step 3: fill contact details and submit.
  async fillContactForm(data: ContactFormData): Promise<void> {
    await this.page.getByRole('textbox', { name: /nombre|name/i }).fill(data.fullName);
    await this.page.getByRole('textbox', { name: /email|correo/i }).fill(data.email);
    if (data.phone) {
      await this.page.getByRole('textbox', { name: /teléfono|phone/i }).fill(data.phone);
    }
    if (data.specialRequests) {
      await this.page.getByRole('textbox', { name: /peticiones|requests/i }).fill(data.specialRequests);
    }
  }

  async acceptPrivacyPolicy(): Promise<void> {
    await this.page.getByRole('checkbox').check();
  }

  async submit(): Promise<void> {
    await this.page.getByRole('button', { name: /confirmar|confirm|enviar|send/i }).click();
  }

  // Asserts that Step 1 landmark is visible — used by the example spec.
  async assertStep1Visible(): Promise<void> {
    await this.page.waitForSelector('[data-slot="card"]', { timeout: 10_000 });
  }
}
