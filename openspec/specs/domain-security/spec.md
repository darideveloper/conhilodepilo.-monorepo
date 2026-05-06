# domain-security Specification

## Purpose
TBD - created by archiving change setup-local-subdomains. Update Purpose after archive.
## Requirements
### Requirement: Domain-Based Security Policies
The backend SHALL implement security policies (CORS, CSRF, and Allowed Hosts) that support the nested subdomain architecture.

#### Scenario: Cross-Subdomain API Access (CORS)
- **Given** the Dashboard is running at `dashboard.conhilodepilo.localhost`
- **When** the Booking app (`booking.conhilodepilo.localhost`) or Landing app (`landing.conhilodepilo.localhost`) makes an API request
- **Then** the Dashboard SHALL allow the request based on the `CORS_ALLOWED_ORIGINS` configuration.

#### Scenario: Secure State Mutations (CSRF)
- **Given** a user is interacting with the Dashboard admin or a frontend form
- **When** a POST/PUT/DELETE request is made
- **Then** the Dashboard SHALL validate the request origin against `CSRF_TRUSTED_ORIGINS`.

#### Scenario: Host Header Validation (ALLOWED_HOSTS)
- **Given** an incoming request to the Dashboard
- **When** the Host header is evaluated
- **Then** the Dashboard SHALL only process the request if the host is in `ALLOWED_HOSTS`.

