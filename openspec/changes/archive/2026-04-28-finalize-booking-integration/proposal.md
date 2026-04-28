# Change: Finalize Booking Integration

## Why
Currently, the booking flow lacks crucial functionality to be complete. It does not allow users to select specific time slots, collects unnecessary fields (number of persons), lacks a backend endpoint to save bookings, and has an incomplete success screen. This change implements the final required integrations.

## What Changes
- Implement time slot selection in the frontend calendar.
- Remove the unused "guests" field from the UI, store, and API payload.
- Update the API payload to include the selected date and time.
- Add a new `CreateBookingView` POST endpoint in the backend.
- Update the `CompanyProfile` model with a configurable privacy policy link and read it in the frontend.
- Provide a final confirmation summary screen.
- Catch API errors and display user-friendly feedback on form submission failure.
- Add unit tests for the booking creation API to ensure validation and processing logic works.

## Impact
- Affected specs: `booking-ui`, `backend-models`, `api-contracts`
- Affected code: Frontend components (`BookingCalendar.tsx`, `BookingForm.tsx`), store (`useBookingStore.ts`), API definitions (`booking.ts`), Backend models (`models.py`), Backend views (`views.py`), and Backend tests (`tests_api.py`).
