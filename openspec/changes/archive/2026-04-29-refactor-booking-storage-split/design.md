# Design: Hybrid Booking Data Persistence

## Context
The `useBookingStore` uses Zustand's `persist` middleware. By default, this middleware uses a single `StateStorage` (localStorage). To meet the requirement of splitting data between `localStorage` and `sessionStorage`, we will implement a custom `StateStorage` router.

## Architectural Decisions

### Decision: Updated `partialize` Logic
To ensure that transient loading and error states are not persisted (which can cause UI glitches on reload), we will update the `partialize` exclusion list in the `persist` middleware.

**Excluded from Persistence**:
- `config`, `services`, `visibility`
- `isConfigLoading`, `isServicesLoading`, `isAvailabilityLoading`, `isSlotsLoading`
- `availabilityError`

### Decision: Custom `hybridStorage` Router
Instead of splitting the store into two (which would require massive refactoring of component selectors), we will create a custom storage object that satisfies the `StateStorage` interface.

**Internal Logic of `hybridStorage`**:
- `setItem(name, value)`:
  - Parses the state string (Zustand provides the entire partialized state).
  - Splits the `state` object into `localPart` and `sessionPart` based on the Data Routing Map.
  - Saves `localPart` to `localStorage` using `${name}-local`.
  - Saves `sessionPart` to `sessionStorage` using `${name}-session`.
- `getItem(name)`:
  - Retrieves from both `localStorage` and `sessionStorage`.
  - Merges the two objects. Special care is taken for `formData` to ensure a deep merge (preserving local identity while applying session-specific service selection).
  - Returns the JSON string of the merged state.
- `removeItem(name)`:
  - Removes both keys.

### Decision: Data Routing Map
We will define a map to ensure consistent routing during `setItem` and `getItem`.

| Property | Storage Backend |
|---|---|
| `language` | `localStorage` |
| `theme` | `localStorage` |
| `formData.fullName` | `localStorage` |
| `formData.email` | `localStorage` |
| `formData.phone` | `localStorage` |
| `selectedDate` | `sessionStorage` |
| `selectedTime` | `sessionStorage` |
| `currentStep` | `sessionStorage` |
| `formData.selectedServices` | `sessionStorage` |
| `formData.serviceGroup` | `sessionStorage` |
| `formData.lockedGroupId` | `sessionStorage` |
| `formData.specialRequests` | `sessionStorage` |
| `formData.privacyAccepted` | `sessionStorage` |
| `availability` | `sessionStorage` |
| `availableSlots` | `sessionStorage` |

### Decision: Exclusive Service Selection from URL/Props
When the booking app is integrated as an iframe in a landing page, navigating between different service pages within the same browser session could lead to "service stacking" due to `sessionStorage` persistence.

To prevent this, the `BookingFlow` initialization logic will be updated:
- If an `initialServiceId` (via props) or a `service`/`tour` query parameter is present, it will **overwrite** the `selectedServices` in the store instead of appending to them.
- This ensures that a landing page navigation always results in a clean selection of exactly the requested service, while still benefiting from the `localStorage` persistence of user identity fields.

## Risks and Trade-offs

| Risk | Mitigation |
|---|---|
| Deep Nesting in `formData` | The hybrid storage engine must handle deep merging of the `formData` object to avoid overwriting the entire object when one part is loaded. |
| Rehydration Timing | Since we are merging two sources, we must ensure the `onRehydrateStorage` hook (which handles Date revival) operates on the final merged state. |
| Key Collision | We will use a unique key (e.g., `booking-hybrid-storage`) to avoid conflicts with the previous `booking-storage` key during transition. |

## Implementation Details

The `hybridStorage` will be defined inside `useBookingStore.ts` to keep it close to the state definition.

```typescript
const hybridStorage: StateStorage = {
  getItem: (name) => {
    const local = localStorage.getItem(`${name}-local`);
    const session = sessionStorage.getItem(`${name}-session`);
    // ... merge logic
  },
  setItem: (name, value) => {
    // ... split logic
    localStorage.setItem(`${name}-local`, JSON.stringify(localPart));
    sessionStorage.setItem(`${name}-session`, JSON.stringify(sessionPart));
  },
  removeItem: (name) => {
    localStorage.removeItem(`${name}-local`);
    sessionStorage.removeItem(`${name}-session`);
  }
};
```
