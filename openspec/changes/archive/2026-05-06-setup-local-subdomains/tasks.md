# Task Roadmap: Backend & Nested Subdomain Setup

## Phase 1: Dashboard Security & Config
- [x] Update `dashboard/project/settings.py` to handle `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` from environment variables.
- [x] Update `dashboard/.env.example` and existing `.env` files to include:
    - `ALLOWED_HOSTS=dashboard.conhilodepilo.localhost,localhost`
    - `CORS_ALLOWED_ORIGINS=https://booking.conhilodepilo.localhost,https://landing.conhilodepilo.localhost`
    - `CSRF_TRUSTED_ORIGINS=https://dashboard.conhilodepilo.localhost,https://booking.conhilodepilo.localhost,https://landing.conhilodepilo.localhost`

## Phase 2: Orchestration
- [x] Update root `dev.sh` to use:
    - `portless dashboard.conhilodepilo` for Django.
    - `portless booking.conhilodepilo` for Booking.
    - `portless landing.conhilodepilo` for Landing.
- [x] Update `package.json` scripts in `booking` and `landing` to match the new nested naming (`booking.conhilodepilo` and `landing.conhilodepilo`).

## Phase 3: Frontend Integration & Connectivity
- [x] Update `booking/.env.dev` (and `.env.example`) to use `https://dashboard.conhilodepilo.localhost` as the API URL.
- [x] Update `landing/.env.dev` (and `.example`) to use `https://dashboard.conhilodepilo.localhost` as the API URL.
- [x] Ensure all frontend API service calls correctly reference the environment-driven API URL.

## Phase 4: Validation & Stability
- [ ] Verify `https://dashboard.conhilodepilo.localhost` resolves and serves the admin panel.
- [ ] Verify `https://booking.conhilodepilo.localhost` resolves and can fetch services from the backend.
- [ ] Verify `https://landing.conhilodepilo.localhost` resolves and can fetch content from the backend.
- [ ] Confirm no CORS errors occur when the Booking app submits a reservation to the Dashboard.
- [ ] Confirm no CSRF errors occur when interacting with the Dashboard admin.