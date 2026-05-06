# Proposal: Complete Local Subdomain Setup for Backend

## Motivation
Frontend projects (`booking` and `landing`) already have portless subdomains working. To provide a professional development environment that closely mirrors production (e.g., `dashboard.conhilodepilo.com`), we will transition to a nested subdomain structure: `dashboard.conhilodepilo.localhost`, `booking.conhilodepilo.localhost`, and `landing.conhilodepilo.localhost`. This ensures a consistent development experience and supports cross-origin requests and webhooks with production-like URLs.

## Scope
- Configuring `dashboard.conhilodepilo.localhost` (Django) using `portless`.
- Updating frontend projects to use `booking.conhilodepilo.localhost` and `landing.conhilodepilo.localhost`.
- **Security Configuration**: Implementing environment-driven `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` in Django to ensure secure communication between subdomains.
- Updating `dev.sh` to:
    - Utilize `portless` for all services with the new nested names.
    - Maintain `tmux` orchestration for the multi-service stack.
- Updating all `.env` files across the monorepo to point to these new nested subdomains and configure security origins.

## Out of Scope
- Modifying frontend `portless` configurations (already working).
- Actually purchasing the domains or setting up production DNS records.