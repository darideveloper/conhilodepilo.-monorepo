# Backend Domain Routing and Local Tunnel Design

## Context
The ecosystem consists of three services. While the frontends (`booking` and `landing`) already use `portless`, the **Dashboard** (Django API and admin) still runs on a standard port. To provide a consistent development experience and support HTTPS locally for all services, the Dashboard must also use `portless`.

## Domain Architecture
The intended local subdomains are:
- `booking.conhilodepilo.localhost` -> Routes to the Booking frontend app.
- `landing.conhilodepilo.localhost` -> Routes to the Landing frontend app.
- `dashboard.conhilodepilo.localhost` -> Routes to the Django Dashboard & API.

## Security Configuration
To ensure secure and functional cross-subdomain communication, the Django backend will be configured as follows:
- **`ALLOWED_HOSTS`**: Must include `dashboard.conhilodepilo.localhost` and `localhost`.
- **`CORS_ALLOWED_ORIGINS`**: Must include `https://booking.conhilodepilo.localhost` and `https://landing.conhilodepilo.localhost` to allow frontend API requests.
- **`CSRF_TRUSTED_ORIGINS`**: Must include `https://dashboard.conhilodepilo.localhost`, `https://booking.conhilodepilo.localhost`, and `https://landing.conhilodepilo.localhost` to allow secure form submissions and state-changing requests from the frontends.

## Local Orchestration Strategy
The `dev.sh` script will be updated to include `portless` for all services:
1.  **Service Tunneling**:
    - **Dashboard**: `portless dashboard.conhilodepilo --app-port 8000 -- python manage.py runserver`
    - **Booking**: `portless booking.conhilodepilo --app-port 3000 -- npm run dev`
    - **Landing**: `portless landing.conhilodepilo --app-port 4321 -- npm run dev`
2.  **Environment Variables**:
    - **Dashboard**: `settings.py` will use env vars for `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS`.
    - **Frontends**: Their `.env` files will be updated to use `https://dashboard.conhilodepilo.localhost` as the API URL.