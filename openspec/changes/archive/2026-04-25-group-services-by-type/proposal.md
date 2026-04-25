# Proposal: Group Services by Type and Filter UI

## Problem Statement
The booking system currently displays all service categories (Event Types) in a single list. As the catalog grows (e.g., adding professional training courses alongside salon treatments), it becomes necessary to segment these services to improve user experience and ensure that prefilled flows (e.g., coming from a "Courses" landing page) remain focused on the relevant category group.

## Proposed Solution
Introduce a grouping layer for `EventType` in the backend and implement group-based filtering in the frontend. When a service is prefilled via URL, the system will identify its group and lock the UI to only show related service types.

### 1. Backend: Model & API Evolution
- **New Model:** `EventTypeGroup` (id, name).
- **Schema Update:** Add a `group` field (ForeignKey) to `EventType`.
- **API Extension:** Include `group_id` in the `EventTypeSerializer` response.
- **Data Migration:** Create initial groups ("Courses" and "Salon Services") and assign existing categories based on their names.

### 2. Frontend: Group-Aware Selection
- **State Management:** Add `lockedGroupId` to `BookingState` in `useBookingStore`.
- **Filtering Logic:** 
    - On initialization, if a `service` is prefilled, find its group.
    - If a group is found, set `lockedGroupId`.
    - Filter the `servicesData` array in `BookingServiceSelection` to only show categories matching `lockedGroupId`.
- **Persistence:** The lock remains active even if the prefilled service is removed, ensuring the user stays within the intended flow.

## Architectural Reasoning
- **Backend-Driven Filtering:** Storing the group relationship in the database allows for easy management via the Django Admin.
- **Locked UI State:** By locking the group, we prevent "category contamination" where a user might accidentally mix professional courses with quick salon treatments in a single booking session.
- **Graceful Fallback:** If no service is prefilled, or the service has no group, all options remain available.
