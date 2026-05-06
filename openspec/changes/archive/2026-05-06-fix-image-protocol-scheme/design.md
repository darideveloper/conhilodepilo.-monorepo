# Design: Fix Image Protocol Scheme

## Context
The project uses `portless` for local development with subdomains. `portless` acts as a reverse proxy that provides SSL. When a request reaches Django, it has already been decrypted, so Django sees it as a plain `http` request.

## Technical Details
Django's `request.is_secure()` method checks the `SECURE_PROXY_SSL_HEADER` setting. If set, it looks for the specified header in the incoming request. If the header matches the expected value, `is_secure()` returns `True`.

### Configuration
In `dashboard/project/settings.py`:
```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

Note: Django prepends `HTTP_` to headers and converts them to uppercase when accessing them from the meta dictionary. `X-Forwarded-Proto` becomes `HTTP_X_FORWARDED_PROTO`.

## Impact
- **Media URLs**: DRF serializers using `request.build_absolute_uri()` will now correctly generate `https://` links.
- **Security**: Ensures `is_secure()` returns the correct value, which is important for other security features (like secure cookies) if enabled in the future.
