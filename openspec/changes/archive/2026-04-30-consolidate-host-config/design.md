# Design: Single Host Configuration

## Overview
The goal is to move from a dual-variable setup (`HOST` and `SITE_URL`) to a single `HOST` variable in the backend.

## Architectural Changes

### 1. Environment Variable Mapping
- **Input**: `HOST` (e.g., `https://api.example.com` or `http://localhost:8000`)
- **Mapping**: In `backend/project/settings.py`, `HOST` will be read using `os.getenv("HOST")`.

### 2. Setting Consolidation
The `SITE_URL` setting will be deprecated and removed in favor of `HOST`. Any code previously relying on `settings.SITE_URL` will be updated to use `settings.HOST`.

### 3. Automatic ALLOWED_HOSTS Inclusion
To simplify configuration, `settings.py` will extract the hostname from `settings.HOST` and add it to the `ALLOWED_HOSTS` list if it's not already there.

```python
from urllib.parse import urlparse

HOST = os.getenv("HOST", "")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

if HOST:
    host_name = urlparse(HOST).hostname
    if host_name and host_name not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host_name)
```

### 4. Dockerfile Integration
The `HOST` variable will be added as an `ARG` and `ENV` in the `Dockerfile` to allow it to be passed during build or set as a default in the container.

### 5. File Updates

#### `backend/project/settings.py`
- Replace `SITE_URL = os.getenv("SITE_URL")` with `HOST = os.getenv("HOST")`.
- Implement automatic `ALLOWED_HOSTS` logic.

#### `backend/utils/stripe_utils.py`
- Replace `settings.SITE_URL` with `settings.HOST`.

#### `backend/Dockerfile`
- Add `ARG HOST` and `ENV HOST=${HOST}`.

### 6. Compatibility
Since `SITE_URL` is a common variable name, we will ensure that `settings.HOST` is the single source of truth for the backend's external-facing URL. If other settings (like `UNFOLD["SITE_URL"]`) need absolute paths, they will continue to use their specific configurations (which are currently relative `/` for Unfold).

## Implementation Strategy
1.  Update `settings.py` to include `HOST` and `ALLOWED_HOSTS` logic.
2.  Update `stripe_utils.py` to use `settings.HOST`.
3.  Update `Dockerfile` to include `HOST`.
4.  Cleanup `.env` files and templates.
5.  Verify `media.py` works as expected.
