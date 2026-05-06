# Proposal: Fix Image Protocol Scheme

## Problem
The backend returns image URLs with `http://` instead of `https://` in the API responses (e.g., `/api/services/`). This happens because the Django application is running behind a proxy (`portless`) that terminates SSL and forwards requests over `http`. Django doesn't recognize the original request was `https`, so it generates `http` absolute URIs for media files.

## Proposed Solution
Enable Django's `SECURE_PROXY_SSL_HEADER` setting. This allows Django to trust a specific header (usually `X-Forwarded-Proto`) sent by the proxy to determine the original protocol.

## Scope
- **Dashboard (Django)**: Update `settings.py` to include `SECURE_PROXY_SSL_HEADER`.
- **OpenSpec**: Update `domain-security` spec to reflect this requirement.

## Alternatives Considered
- **Forcing HOST prefix**: Manually prepending `HOST` to all media URLs. This is brittle and bypasses Django's built-in URI generation logic.
- **Middleware**: Custom middleware to rewrite URLs. Unnecessary since Django has a built-in setting for this exact scenario.
