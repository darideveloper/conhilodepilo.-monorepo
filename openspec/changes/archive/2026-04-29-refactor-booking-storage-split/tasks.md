# Tasks: Hybrid Booking Data Persistence

- [x] Implementation of `hybridStorage` engine in `useBookingStore.ts` <!-- id: 0 -->
    - [x] Define the routing map for local/session fields.
    - [x] Implement `getItem`, `setItem`, and `removeItem`.
- [x] Refactor `useBookingStore` configuration <!-- id: 1 -->
    - [x] Update `persist` middleware to use `hybridStorage`.
    - [x] Update `partialize` to exclude all loading and error states (`isAvailabilityLoading`, `isSlotsLoading`, `availabilityError`).
    - [x] Change storage key to `booking-hybrid-storage`.
    - [x] Update `resetBooking` action to preserve personal data.
- [x] Implement Exclusive Service Selection <!-- id: 3 -->
    - [x] Pass `initialServiceId` to `BookingFlow` in `src/components/pages/index.astro`.
    - [x] Update `BookingFlow.tsx` initialization to overwrite `selectedServices` when a specific service is requested via URL or props.

- [x] Validation and Testing <!-- id: 2 -->
    - [x] Verify personal data persists after `resetBooking`.
    - [x] Verify personal data persists after page refresh.
    - [x] Verify booking session data is cleared after closing and reopening the tab.
    - [x] Verify `currentStep` resets to 1 in a new tab but persists on refresh.
