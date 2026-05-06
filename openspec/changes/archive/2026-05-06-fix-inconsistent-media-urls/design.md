# Design: Absolute Media URL Resolution in API

## Architecture Overview
Django REST Framework (DRF) by default uses `request.build_absolute_uri()` to generate URLs for `ImageField` and `FileField`. This method relies on the `META['HTTP_HOST']` or `META['SERVER_NAME']` of the current request.

To provide a consistent experience, we will override this behavior by creating a custom serializer field that prioritizes the `HOST` environment variable (via `settings.HOST`) while still providing a safe fallback.

## Components

### 1. `AbsoluteImageField` (Serializer Field)
A new class `AbsoluteImageField` will be added to `dashboard/utils/media.py`. It prioritizes the `HOST` environment variable while falling back to request-based URLs if `HOST` is not configured.

**Refined Logic:**
```python
class AbsoluteImageField(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None
        
        # If HOST is set, use the specialized utility
        if getattr(settings, 'HOST', None):
            return get_media_url(value)
            
        # Fallback to default DRF behavior (request-based) if HOST is missing
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(value.url)
        return value.url
```

### 2. Serializer Updates
The following serializers in `dashboard/booking/serializers.py` will be updated. The fields MUST be explicitly declared in the serializer class to override the default `ModelSerializer` behavior:

- `CompanyProfileSerializer`: Add `logo = AbsoluteImageField(read_only=True)`
- `EventSerializer`: Add `image = AbsoluteImageField(read_only=True)`
- `EventTypeSerializer`: Add `image = AbsoluteImageField(read_only=True)`

## Trade-offs
- **Pros**: Guarantees URL consistency; fixes broken images in SSR; centralizes URL logic.
- **Cons**: Slightly deviates from standard DRF "request-aware" behavior, which might be unexpected if the system were to support multiple canonical domains (which it currently does not).
