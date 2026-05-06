# Change: Fix Inconsistent Media URLs in API

## Why
The current API returns media URLs (logos, images) based on the `Host` header of the request, which leads to broken images in frontend SSR or when accessed via internal IPs. We need to enforce the use of the canonical `HOST` setting.

## What Changes
- Implement `AbsoluteImageField` in `dashboard/utils/media.py` to prepend `settings.HOST` to relative media URLs.
- Update `CompanyProfileSerializer`, `EventSerializer`, and `EventTypeSerializer` in `dashboard/booking/serializers.py` to use `AbsoluteImageField` for all image fields.

## Impact
- Affected specs: `dashboard-host`, `media-resolution`
- Affected code: `dashboard/utils/media.py`, `dashboard/booking/serializers.py`
- **Remote Storage Compatibility**: Fully compatible with AWS S3 and DigitalOcean Spaces; it preserves their absolute URLs while fixing local media paths to use the canonical domain.
