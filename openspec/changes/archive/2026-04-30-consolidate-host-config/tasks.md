# Tasks: Consolidate Host Configuration

- [x] **Research & Validation**
    - [x] Confirm no other hidden usages of `SITE_URL` exist in the backend.
    - [x] Verify if any frontend components rely on the backend's `SITE_URL` via an API response.

- [x] **Implementation**
    - [x] **Settings Refactor**: Modify `backend/project/settings.py` to:
        - Add `HOST = os.getenv("HOST")`.
        - Remove `SITE_URL = os.getenv("SITE_URL")`.
        - Add logic to automatically include `HOST` hostname in `ALLOWED_HOSTS`.
    - [x] **Stripe Utils Update**: Modify `backend/utils/stripe_utils.py` to use `settings.HOST`.
    - [x] **Dockerfile Update**: Add `HOST` to `backend/Dockerfile` as an `ARG` and `ENV`.
    - [x] **Environment Cleanup**:
        - [x] Update `backend/.env.dev` (Remove `SITE_URL`).
        - [x] Update `backend/.env.prod` (Remove `SITE_URL`).
        - [x] Update `backend/.env.dev.example` (Remove `SITE_URL`).
        - [x] Update `backend/.env.prod.example` (Remove `SITE_URL`).

- [x] **Verification**
    - [x] Run backend tests to ensure `media.py` and `stripe_utils.py` don't break.
    - [x] Manually verify a media URL generation (via `python manage.py shell`).
    - [x] Verify `ALLOWED_HOSTS` includes the `HOST` hostname.
    - [x] Run `openspec validate consolidate-host-config --strict`.
