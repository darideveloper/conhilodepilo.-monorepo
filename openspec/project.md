# Project Context

## Purpose
The `conhilorepilo` ecosystem is a multi-service platform consisting of a Django-based management dashboard/API, a Con Hilo Depilo beauty-services landing page, and a booking application. The booking app (originally scaffolded as "granada-go-tours") is the shared appointment-booking UI that connects to the Django backend.

## Shared Architecture
- **Backend:** Python/Django (Dashboard & API)
- **Frontend:** Astro (SSG/SSR) with React integration
- **Versioning/CI:** Monorepo with service-level directories (`backend/`, `landing/`, `booking/`)

## Global Conventions

### Git Workflow
- **Commit Format:** Strictly follows [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): subject`.
- **Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

### Environment Management
- Two-level `.env` system: `.env` sets the `ENV` variable (`dev` or `prod`); `.env.{dev|prod}` holds environment-specific secrets.
- All services use `python-dotenv` (backend) or Vite `loadEnv` (frontend) to load env vars.
- Example files (`.env.example`, `.env.dev.example`, `.env.prod.example`) are committed; actual secret files are not.

### Timezone & i18n
- **Timezone:** `Europe/Madrid` in production; all datetime logic assumes Madrid time.
- **Languages:** Spanish (`es`) is primary; English (`en`) is supported. Admin UI and models are fully translated to Spanish via `locale/es/LC_MESSAGES/`.

### Documentation (OpenSpec)
- **Global:** Cross-service architecture, API contracts, and global dependencies are defined in `openspec/`.
- **Local:** Implementation-level details for each service remain in their respective `/openspec` folders.

---

# Service: Backend (Dashboard & API)

## Purpose
A Django-based administration dashboard and REST API that manages the entire ecosystem: service catalog, bookings, availability, company configuration, and external integrations.

## Directory
`backend/`

## Tech Stack
- **Framework:** Python 3.12, Django 5.2+
- **API:** Django REST Framework (DRF) with Token + Session authentication
- **Admin UI:** Django Unfold (Tailwind-based, fully translated to Spanish)
- **Database:** PostgreSQL (production), SQLite (development/testing)
- **ORM extras:** `django-solo` for singleton models, `django-filter` for dynamic API filtering
- **Storage:** Local filesystem (dev) / AWS S3 via `django-storages` + `boto3` (prod). Three storage backends: `PublicMediaStorage`, `StaticStorage`, `PrivateMediaStorage`.
- **Static files:** WhiteNoise for production static serving
- **Images:** Pillow for image processing
- **Email:** SMTP backend (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, etc.)
- **External integrations:** Stripe (payments), Google Calendar (booking sync)

## Data Model Overview
- `CompanyProfile` (singleton) — company identity, brand color, Stripe keys, Google Calendar ID, booking cooldown, UI labels
- `EventTypeGroup` / `EventType` / `Event` — service catalog (grouped services with pricing, duration, payment model)
- `CompanyAvailability` / `CompanyWeekdaySlot` / `CompanyDateOverride` — company-level availability scheduling
- `EventAvailability` / `AvailabilitySlot` / `EventDateOverride` — per-service availability scheduling
- `Booking` — appointments; linked to services (M2M), stores Stripe payment ID and Google Calendar event ID

## Key Conventions
- **Configuration:** Strictly environment-variable-first (`python-dotenv`). Two-level `.env` system.
- **API Standards:** Centralized error handling (`project/handlers.py`) and metadata-rich pagination (`project/pagination.py`).
- **Auth:** DRF Token authentication (primary) + Session authentication (admin).
- **Testing:** Django test framework with SQLite test DB. Selenium for E2E/browser tests. Test files follow `tests*.py` naming per app.
- **Synchronization:** API endpoint changes MUST be accompanied by updates to automated tests and Bruno OpenCollection files (`bruno/**/*.yml`).
- **Signals:** M2M changes on `Booking.services` auto-recalculate `end_time` via signal.

## Integrations

### Stripe
- Payment model per `EventType`: `PRE-PAID` (Stripe Checkout) or `POST-PAID` (direct confirmation).
- Keys configured per `CompanyProfile` in settings (env vars: `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`).
- Webhook at `/stripe/webhook/` listens for `checkout.session.completed` → sets booking to `PAID` → syncs to Google Calendar.

### Google Calendar
- Single Service Account manages all calendars (credentials via `GOOGLE_CALENDAR_ID` env var).
- Bookings auto-sync via Django signals (`post_save`, `post_delete`).
- **End Time Sync:** `Booking.end_time` is automatically recalculated whenever `start_time` or `services` change, ensuring calendar events stay accurate during rescheduling.
- **Duplication Prevention:** Initial sync is skipped during the first `post_save` (creation) to wait for services to be attached; sync only occurs once complete data is available. Sync logic updates the in-memory instance to prevent race conditions during rapid updates.
- **Admin UI:** Fully translated to Spanish, including custom actions ("Reintentar sincronización con Google Calendar") and status badges.
- `Booking.google_event_id` stores the calendar event ID; self-healing on 404 (re-creates deleted events).

---

# Service: Landing (Con Hilo Depilo)

## Purpose
The marketing and landing page for the Con Hilo Depilo beauty services business (eyebrow threading, lash lifting, hair removal treatments, and training academy).

## Directory
`landing/`

## Tech Stack
- **Framework:** Astro 6 (SSG), TypeScript
- **Styling:** Tailwind CSS v4
- **React:** React 19 (for interactive islands)
- **UI extras:** Swiper (image carousels/gallery), Lucide Astro (icons)
- **Fonts:** `@fontsource-variable/inter` + `@fontsource/inter`
- **Testing:** Vitest
- **Sitemap:** `@astrojs/sitemap` integration
- **Site URL:** `https://conhilodepilo.com`
- **API:** Fetches images and media from the Django backend (`PUBLIC_API_URL` env var)

## Service-Specific Conventions
- **Language:** Spanish (es) is the only UI language.
- **Styling:** Preference for `clsx` for conditional classes (no `class:list`).
- **Output:** Static site generation (SSG). No server adapter needed.
- **Tests:** Vitest for unit/component tests.

---

# Service: Booking Application

## Purpose
An SSR booking application for scheduling appointments. Handles service selection, date/time selection, customer form submission, and real-time availability checking against the Django backend.

## Directory
`booking/` (package name: `granada-go-tours`; dev port alias: `booking`)

## Tech Stack
- **Framework:** Astro 5 (SSR), TypeScript
- **Output:** Server-side rendered via `@astrojs/node` (standalone mode)
- **Styling:** Tailwind CSS v4
- **React:** React 19 (all interactive UI is React)
- **State management:** Zustand (`useBookingStore`)
- **UI components:** Radix UI primitives + shadcn/ui-style components (atoms under `src/components/atoms/ui/`)
- **Icons:** Lucide React
- **Date handling:** `date-fns`, `react-day-picker`
- **Fonts:** `@fontsource/playfair-display`, `@fontsource/lato`
- **Animations:** `tailwindcss-animate`

## Component Architecture
Follows atomic design:
- `atoms/` — primitive UI: `button`, `input`, `calendar`, `badge`, `select`, `textarea`, `label`, `checkbox`, `ThemeToggle`, `LanguageToggle`, `AppLoader`
- `molecules/` — composed: `BookingHeader`, `StatusDetails`, `StatusLegend`
- `organisms/` — full features: `BookingFlow`, `BookingCalendar`, `BookingForm`, `BookingServiceSelection`
- `pages/` — Astro page-level components
- `layouts/` — `Layout.astro`

## API Layer
Located in `src/lib/api/`:
- `client.ts` — base fetch wrapper
- `availability.ts` — availability-specific helpers
- `endpoints/booking.ts`, `endpoints/services.ts`, `endpoints/config.ts` — typed endpoint callers
- `types.ts` — shared API types

## i18n
- Built-in lightweight i18n: `src/lib/i18n/translations.ts` (string map) + `src/lib/i18n/useTranslation.ts` (hook).
- Supports language toggle at runtime (`LanguageToggle` atom).

## Service-Specific Conventions
- **Component strategy:** `.astro` for static/layout UI, `.tsx` for all interactive components.
- **Styling:** Scoped `<style>` tags for Astro; standard CSS/Tailwind utilities for React. Preference for `clsx` + `tailwind-merge` (`cn()` util).
- **State:** All booking wizard state lives in Zustand (`src/store/useBookingStore.ts`).
- **Routes:** `src/pages/index.astro` (home/redirect) and `src/pages/[id].astro` (company-specific booking page).
