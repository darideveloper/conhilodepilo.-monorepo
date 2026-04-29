# Proposal: add-google-calendar-sync

## Summary
Implement full Google Calendar synchronization for bookings with a focus on data integrity and localization. Every time a `Booking` is created (once services are attached), updated (including rescheduling), or deleted, the corresponding event is synchronized with a centralized Google Calendar. The implementation includes automatic end-time recalculation, duplication prevention, and a fully localized Spanish admin interface.

## Motivation
The business owner manages appointments in the Django admin and needs those appointments to automatically reflect in their Google Calendar. The client should receive read-only shared access to the same calendar. Email notifications to clients are handled separately via SMTP, so Google Calendar's native email notifications must be suppressed.

## Why
Google Calendar sync is essential for operational efficiency, allowing the business owner to see their schedule on mobile devices and other apps without logging into the Django admin.

## What Changes
- Adds a new service layer for Google Calendar interaction.
- Extends the `Booking` model to track sync status.
- Implements automated sync triggers via Django signals.
- Enhances the Admin UI with a dedicated sync tab and status indicators.

## Scope

### In scope
- New `backend/utils/google_calendar.py` service layer (auth, event mapping, insert/patch/delete)
- Three new `Booking` model fields: `google_sync_status`, `google_sync_error`, `last_synced_at`
- Django `post_save` / `post_delete` signals on `Booking` to trigger sync automatically
- **Automatic End Time Recalculation:** `Booking.save()` override to keep `end_time` in sync with `start_time`.
- **Duplication Prevention:** Signal logic to skip initial empty syncs and in-memory instance updates.
- Dedicated **"Google Calendar"** tab in `BookingAdmin`.
- **Full Localization:** Spanish translation for all sync-related admin actions and messages.
- `GOOGLE_SERVICE_ACCOUNT_JSON` env var + settings entry (complements existing `GOOGLE_CALENDAR_ID`)
- `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` added to `requirements.txt`
- Admin action "Retry Google Calendar Sync" on the `Booking` list view
- Self-healing: if `patch` returns 404, automatically re-create the event

### Out of scope
- Per-tenant (multi-company) calendar provisioning — project is single-company
- Stripe webhook → calendar sync (Stripe not yet active in this project)
- Frontend calendar embed or display
- Manual steps in Google Cloud Console / Calendar sharing (documented but not automated)

## Pre-requisites (manual, non-code)
1. **Google Cloud Console**: create a project, enable the Google Calendar API, create a Service Account, and download its JSON key.
2. **Google Calendar**: add the Service Account email as an editor on the target calendar.
3. **Client sharing**: share the calendar with the client's email (view-only) via Google Calendar settings.
4. **`.env`**: populate `GOOGLE_CALENDAR_ID` (already in settings) and `GOOGLE_SERVICE_ACCOUNT_JSON` (full JSON string or file path).

## Architecture
See `design.md` for details.

## Spec Deltas
| Capability | Delta Type | File |
|---|---|---|
| `google-calendar-service` | ADDED | `specs/google-calendar-service/spec.md` |
| `booking-google-sync` | ADDED | `specs/booking-google-sync/spec.md` |
| `admin-booking-google-tab` | ADDED | `specs/admin-booking-google-tab/spec.md` |

## Open Questions
None — all ambiguities resolved based on Gemini analysis and user constraints.
