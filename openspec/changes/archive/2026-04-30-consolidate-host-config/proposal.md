# Proposal: Consolidate Backend Host Configuration

## Problem
The backend currently uses two separate environment variables, `HOST` and `SITE_URL`, which often hold the same value. Furthermore, `HOST` is used in `backend/utils/media.py` but is not actually defined as a setting in `backend/project/settings.py`, while `SITE_URL` is defined in settings but not used in `media.py`. This redundancy and inconsistency lead to confusion, potential runtime errors, and duplication of values in environment files.

## Proposed Solution
Consolidate both environment variables into a single `HOST` variable. This variable will be the single source of truth for the backend's base URL (including protocol and port if applicable).

### Key Changes:
1.  **Refactor Settings**: Update `backend/project/settings.py` to load `HOST` from the environment and remove `SITE_URL`. 
2.  **Unify Usage**: Update all backend code (specifically `stripe_utils.py`) to use `settings.HOST` instead of `settings.SITE_URL`.
3.  **Automatic Allowed Hosts**: Enhance `settings.py` to automatically extract the hostname from `HOST` and add it to `ALLOWED_HOSTS` if not already present.
4.  **Dockerfile Update**: Add `HOST` to the `Dockerfile` as an ARG and ENV to ensure consistency in containerized environments.
5.  **Clean Environments**: Remove `SITE_URL` from all `.env` files and templates (`.env.dev`, `.env.prod`, `.env.dev.example`, `.env.prod.example`).
6.  **Fix Bug**: Properly define `HOST` in `settings.py` to satisfy the requirements of `backend/utils/media.py`.

## Benefits
- **Simplicity**: Only one variable to configure for the backend's identity.
- **Consistency**: All utilities use the same setting.
- **Robustness**: Fixes the missing `settings.HOST` attribute that would cause `AttributeError` in `media.py`.
- **Maintainability**: Reduces duplication in `.env` files and simplifies `ALLOWED_HOSTS` configuration.
