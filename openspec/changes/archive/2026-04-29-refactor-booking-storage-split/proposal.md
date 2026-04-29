# Proposal: Hybrid Booking Data Persistence

## Why
Currently, all booking state is persisted in `localStorage`. This causes two main issues:
1. **Stale Booking Data**: If a user leaves a booking half-finished and returns later (or in a new tab), they see their previous (potentially outdated) selection of services, date, and time.
2. **Repetitive Data Entry**: Personal information like name, email, and phone is cleared whenever a booking is reset or finished, forcing repeat customers to re-enter their details.

## What Changes
We will implement a **Hybrid Storage Engine** for the `useBookingStore`. This custom engine will route state properties to either `localStorage` or `sessionStorage` based on their nature:

- **Local Storage (Persistent)**: Reusable user preferences and identity.
  - `language`, `theme`
  - `formData.fullName`, `formData.email`, `formData.phone`
- **Session Storage (Ephemeral)**: Booking-specific selection and transient state.
  - `selectedDate`, `selectedTime`
  - `currentStep`
  - `formData.selectedServices`, `formData.serviceGroup`, `formData.lockedGroupId`, `formData.specialRequests`, `formData.privacyAccepted`
  - `availability` and `availableSlots` (cache)
- **Not Persisted**:
  - `config`, `services`, `visibility`, and all loading/error states (already handled by `partialize`).

### Component Impact
- **`useBookingStore.ts`**: Implements the hybrid storage router.
- **`resetBooking()`**: Updated to preserve the persistent user fields (name, email, phone) while clearing the session fields.
- **`BookingFlow.tsx`**: Implements **Exclusive Service Selection**. When a service is requested via URL or props, it clears previous ephemeral selections to prevent service stacking within the same session.
- **Other components**: No changes required to selectors or imports! They continue to use `useBookingStore` exactly as before.

## Impact
- **User Experience**: Users only enter their contact info once. Each new browser tab/session starts a fresh booking. Refreshing the page preserves the current booking state.
- **Maintainability**: High. The logic is centralized in the store configuration rather than scattered across components.
- **Backward Compatibility**: The first time a user loads the app after this change, they might have to re-enter their info as we transition from the old `booking-storage` key to the new hybrid system. This is a one-time transition.
