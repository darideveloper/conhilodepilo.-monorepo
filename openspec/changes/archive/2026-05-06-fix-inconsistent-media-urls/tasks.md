# Tasks: Fix Inconsistent Media URLs

- [x] **Research and Setup**
    - [x] 1.1 Verify current `settings.HOST` configuration in `.env.dev`.
    - [x] 1.2 Create a reproduction script or manual test case using `curl` with the `Host` header set to an IP address.

- [x] **Implementation**
    - [x] 2.1 Implement `AbsoluteImageField` in `dashboard/utils/media.py`.
    - [x] 2.2 Update `CompanyProfileSerializer` in `dashboard/booking/serializers.py`.
    - [x] 2.3 Update `EventSerializer` in `dashboard/booking/serializers.py`.
    - [x] 2.4 Update `EventTypeSerializer` in `dashboard/booking/serializers.py`.

- [x] **Validation**
    - [x] 3.1 Run `curl -H "Host: 127.0.0.1:8000" http://127.0.0.1:8000/api/config/` and verify `logo` URL.
    - [x] 3.2 Run `curl -H "Host: 127.0.0.1:8000" http://127.0.0.1:8000/api/services/` and verify `image` URLs.
    - [x] 3.3 Ensure existing unit tests for serializers still pass.
