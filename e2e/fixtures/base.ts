import { expect } from '@playwright/test';
import { test as authTest } from './auth.js';

// Single `test` export that composes all custom fixtures.
// Every spec file in this project should import from here, not from @playwright/test.
export const test = authTest;
export { expect };
