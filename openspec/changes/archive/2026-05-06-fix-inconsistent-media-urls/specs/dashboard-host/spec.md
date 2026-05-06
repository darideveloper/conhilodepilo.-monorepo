# dashboard-host Specification

## MODIFIED Requirements

### Requirement: Single Dashboard Host Setting
The dashboard service SHALL use a single `HOST` environment variable to define its base URL and ensure all media URLs in API responses are absolute and point to the canonical domain, regardless of the request's `Host` header.

#### Scenario: Media URL Generation
- **GIVEN** `HOST` is set to `http://localhost:8000`
- **WHEN** a media URL is generated for a local file `/media/test.jpg`
- **THEN** the returned URL SHALL be `http://localhost:8000/media/test.jpg`

#### Scenario: API Media URL Generation via IP
- **GIVEN** `HOST` is set to `https://dashboard.conhilodepilo.localhost`
- **WHEN** a `GET /api/config/` request is made to `http://127.0.0.1:8000/api/config/`
- **THEN** the `logo` URL in the response SHALL be `https://dashboard.conhilodepilo.localhost/media/branding/logo.png`

#### Scenario: API Media URL Generation via Canonical Domain
- **GIVEN** `HOST` is set to `https://dashboard.conhilodepilo.localhost`
- **WHEN** a `GET /api/config/` request is made to `https://dashboard.conhilodepilo.localhost/api/config/`
- **THEN** the `logo` URL in the response SHALL be `https://dashboard.conhilodepilo.localhost/media/branding/logo.png`
