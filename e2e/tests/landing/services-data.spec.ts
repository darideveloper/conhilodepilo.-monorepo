import { test, expect } from '../../fixtures/base.js';
import { fetchServices } from '../../helpers/api.js';
import { LandingPage } from '../../pages/landing/LandingPage.js';

// Full shapes returned by GET /api/services/ (the e2e helper type is a subset).
interface ServiceFull {
  id: number;
  title: string;
  price: string;
  duration: number;
  image: string | null;
  description: string | null;
}

interface CategoryFull {
  id: number;
  name: string;
  description: string | null;
  image: string | null;
  group_id: number;
  services: ServiceFull[];
}

// Mirror the landing's PUBLIC_COURSES_GROUP_ID filter so card-count assertions
// match what the landing actually renders (courses are excluded from #servicios).
const coursesGroupId = process.env['PUBLIC_COURSES_GROUP_ID']
  ? Number(process.env['PUBLIC_COURSES_GROUP_ID'])
  : 2;

test.describe('Landing: services section renders dashboard data', () => {
  let categories: CategoryFull[] = [];

  test.beforeEach(async ({ request }) => {
    const all = (await fetchServices(request)) as unknown as CategoryFull[];
    categories = coursesGroupId != null
      ? all.filter((c) => c.group_id !== coursesGroupId)
      : all;

    if (categories.length === 0) {
      test.skip(
        true,
        'No non-courses service categories in the dashboard — add at least one via the admin UI first',
      );
    }
  });

  test('services section renders correct card count', async ({ page }) => {
    const landing = new LandingPage(page);
    await landing.open();
    await landing.waitForHydration();
    await landing.assertCardCount(categories.length);
  });

  test('first card renders dashboard image, name, and description', async ({ page }) => {
    const firstCategory = categories[0];

    if (!firstCategory.image) {
      test.skip(true, `First category "${firstCategory.name}" has no image uploaded — upload one via the admin UI to test image rendering`);
      return;
    }

    const landing = new LandingPage(page);
    await landing.open();
    await landing.waitForHydration();

    const card = landing.getFirstCard();
    await landing.assertCardImageVisible(card);
    await landing.assertCardImagePlaceholderAbsent(card);
    await landing.assertCardName(card, firstCategory.name);

    if (firstCategory.description) {
      await landing.assertCardDescriptionNonEmpty(card);
    }
  });

  test('first card pill buttons match API service count and first is pre-selected', async ({ page }) => {
    const firstCategory = categories[0];

    const landing = new LandingPage(page);
    await landing.open();
    await landing.waitForHydration();

    const card = landing.getFirstCard();
    await landing.assertServiceButtonCount(card, firstCategory.services.length);
    await landing.assertFirstPillSelected(card);
  });

  test('clicking second pill updates selection, price, and duration', async ({ page }) => {
    const firstCategory = categories[0];

    if (firstCategory.services.length < 2) {
      test.skip(
        true,
        `First category "${firstCategory.name}" has only one service — cannot test pill switching`,
      );
      return;
    }

    const landing = new LandingPage(page);
    await landing.open();
    await landing.waitForHydration();

    const card = landing.getFirstCard();
    const secondService = firstCategory.services[1];

    await expect(async () => {
      await landing.clickServiceButton(card, 1);
      await landing.assertPillSelected(card, 1);
    }).toPass({ timeout: 10_000 });

    const priceText = await landing.getPriceText(card);
    expect(priceText).toContain(secondService.price);

    const durationText = await landing.getDurationText(card);
    expect(durationText).toContain(String(secondService.duration));
  });

  test('Reservar button navigates to /booking/{service.id}', async ({ page }) => {
    const firstCategory = categories[0];
    const firstService = firstCategory.services[0];

    const landing = new LandingPage(page);
    await landing.open();
    await landing.waitForHydration();

    const card = landing.getFirstCard();
    await expect(async () => {
      await landing.clickReservar(card);
      expect(page.url()).toContain(`/booking/${firstService.id}`);
    }).toPass({ timeout: 10_000 });
  });
});
