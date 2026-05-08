import { test, expect } from '../../fixtures/base.js';
import { LoginPage } from '../../pages/dashboard/LoginPage.js';
import { BookingListPage } from '../../pages/dashboard/BookingListPage.js';
import { createBooking, fetchServices, fetchAvailableSlots } from '../../helpers/api.js';
import { toApiDate, daysFromNow } from '../../helpers/dates.js';

// Example integration spec: creates a booking via the public API, then verifies
// it appears in the Django admin booking list.
// Requires both the dashboard service and a configured dev database.

test('created booking is visible in the admin list', async ({ page, adminCredentials, request }) => {
  // 1. Fetch first available service from the API
  const categories = await fetchServices(request);
  const firstService = categories[0]?.services[0];

  if (!firstService) {
    test.skip(true, 'No services available in the dashboard — add one via the admin UI first');
    return;
  }

  // 2. Find an available slot 7 days from now (avoids booking cooldown)
  const targetDate = daysFromNow(7);
  const dateStr = toApiDate(targetDate);
  const slots = await fetchAvailableSlots(request, [firstService.id], dateStr);

  if (!slots.length) {
    test.skip(true, `No availability for service ${firstService.id} on ${dateStr} — configure availability via the admin UI`);
    return;
  }

  // 3. Create a booking via the public booking API.
  // Use a unique client_name — it appears in list_display, unlike client_email.
  const clientName = `E2E Test ${Date.now()}`;
  await createBooking(request, {
    clientName,
    clientEmail: 'e2e-test@example.com',
    service_ids: [firstService.id],
    date: dateStr,
    startTime: slots[0] as string,
  });

  // 4. Log into the Django admin
  const loginPage = new LoginPage(page);
  await loginPage.open();
  await loginPage.login(adminCredentials);
  await loginPage.assertLoggedIn();

  // 5. Navigate to the booking list and assert the row is present
  const bookingList = new BookingListPage(page);
  await bookingList.open();
  await bookingList.assertRowVisible(clientName);
});
