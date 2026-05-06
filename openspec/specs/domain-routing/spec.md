# domain-routing Specification

## Purpose
TBD - created by archiving change setup-local-subdomains. Update Purpose after archive.
## Requirements
### Requirement: Standardized Domain Routing
The system SHALL route requests to the appropriate service based on a standardized subdomain prefix structure.

#### Scenario: Service Routing Definition
- **Given** an incoming request to the platform's root domain (e.g., `conhilodepilo.*`).
- **When** the domain is evaluated.
- **Then** `dashboard.conhilodepilo.*` SHALL route to the Django backend.
- **And** `booking.conhilodepilo.*` SHALL route to the Booking Astro SSR frontend.
- **And** `landing.conhilodepilo.*` SHALL route to the Landing Astro SSG frontend.

