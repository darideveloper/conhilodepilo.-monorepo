import { defineConfig, devices } from '@playwright/test';
import * as dotenv from 'dotenv';

dotenv.config();

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: process.env['CI'] ? 2 : 0,
  reporter: [['html', { open: 'never' }], ['list']],
  use: {
    // Portless serves all local domains over HTTPS with self-signed certs
    ignoreHTTPSErrors: true,
    trace: 'on-first-retry',
    video: 'on-first-retry',
  },
  projects: [
    {
      name: 'booking',
      testMatch: 'tests/booking/**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env['BOOKING_URL'] ?? 'https://booking.conhilodepilo',
      },
    },
    {
      name: 'dashboard',
      testMatch: 'tests/dashboard/**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env['DASHBOARD_URL'] ?? 'https://dashboard.conhilodepilo',
      },
    },
    {
      name: 'landing',
      testMatch: 'tests/landing/**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env['LANDING_URL'] ?? 'https://landing.conhilodepilo',
      },
    },
    {
      name: 'integrations',
      testMatch: 'tests/integrations/**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env['DASHBOARD_URL'] ?? 'https://dashboard.conhilodepilo',
      },
    },
  ],
});
