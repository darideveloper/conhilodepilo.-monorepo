import { test, expect } from '../../fixtures/base.js';
import { LoginPage } from '../../pages/dashboard/LoginPage.js';

// Example spec: proves the dashboard harness can reach the Django admin login page.

test('admin login form is visible', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.open();

  // Django admin always renders a login form at /admin/login/
  await expect(page.locator('#login-form')).toBeVisible();
  await expect(page.locator('#id_username')).toBeVisible();
  await expect(page.locator('#id_password')).toBeVisible();
  await expect(page.getByRole('button', { name: /iniciar sesión/i })).toBeVisible();
});
