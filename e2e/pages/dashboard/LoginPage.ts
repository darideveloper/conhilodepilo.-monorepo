import type { Page } from '@playwright/test';
import { expect } from '@playwright/test';
import type { AdminCredentials } from '../../fixtures/auth.js';

// Page Object for the Django admin login form at /admin/login/.
export class LoginPage {
  constructor(private readonly page: Page) {}

  async open(): Promise<void> {
    // Navigate to /admin/ so Django sets ?next=/admin/ on the login redirect,
    // ensuring a successful login lands back on the admin dashboard (not /accounts/profile/).
    await this.page.goto('/admin/');
  }

  async login(credentials: AdminCredentials): Promise<void> {
    await this.page.locator('#id_username').fill(credentials.username);
    await this.page.locator('#id_password').fill(credentials.password);
    await this.page.getByRole('button', { name: /iniciar sesión/i }).click();
  }

  async assertLoggedIn(): Promise<void> {
    // Unfold admin uses #page / #main as top-level landmarks (no #header)
    await expect(this.page).toHaveURL(/\/admin\//);
    await expect(this.page.locator('#main')).toBeVisible();
  }
}
