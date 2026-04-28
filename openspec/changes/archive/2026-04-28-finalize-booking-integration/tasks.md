## 1. Backend API & Models
- [x] 1.1 Add `privacy_policy_url` to `CompanyProfile` model and `CompanyProfileSerializer`.
- [x] 1.2 Add `special_requests` field to `Booking` model.
- [x] 1.3 Create `CreateBookingView` POST endpoint in `backend/booking/views.py` with validation and time calculations.
- [x] 1.4 Add URL route for `CreateBookingView` to `backend/project/urls.py` (e.g., `api/bookings/`).
- [x] 1.5 Add unit tests for `CreateBookingView` to verify successful booking creation and validation errors.

## 2. Frontend State & API
- [x] 2.1 Update `BookingPayload` in `booking.ts` to include `date` and `startTime` and remove `guests`.
- [x] 2.2 Update `submitBooking` usage to pass the new payload shape.
- [x] 2.3 Update `useBookingStore` to hold `selectedTime`, remove `guests`, and add action to fetch slots for a selected date.
- [x] 2.4 Update `AppConfig` TypeScript interface in `useBookingStore.ts` to include `privacy_policy_url`.

## 3. Frontend UI Updates
- [x] 3.1 Update `BookingCalendar.tsx` to display and allow selecting available time slots once a day is selected.
- [x] 3.2 Update `BookingForm.tsx` to remove the guests input field.
- [x] 3.3 Update `BookingForm.tsx` to use the dynamic `privacy_policy_url` from the store configuration.
- [x] 3.4 Update the success screen in `BookingForm.tsx` to show client info (Name, Email, Time Slot).
- [x] 3.5 Implement error handling in `BookingForm.tsx`'s `handleSubmit` to show user-friendly API errors.
