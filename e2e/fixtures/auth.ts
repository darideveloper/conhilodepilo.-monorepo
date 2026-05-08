import { test as base } from '@playwright/test'

export interface AdminCredentials {
  username: string
  password: string
}

type AuthFixtures = {
  adminCredentials: AdminCredentials
}

export const test = base.extend<AuthFixtures>({
  // Reads from env vars; falls back to the Django dev-server defaults.
  // DASHBOARD_ADMIN_USER / DASHBOARD_ADMIN_PASS are not listed in .env.example
  // because they are optional for running URL-only tests.
  adminCredentials: async ({}, use) => {
    const credentials: AdminCredentials = {
      username: process.env['DASHBOARD_ADMIN_USER'] ?? 'admin',
      password: process.env['DASHBOARD_ADMIN_PASS'] ?? 'admin',
    }
    await use(credentials)
  },
})
