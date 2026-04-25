# Tasks: Group Services by Type

## 1. Backend Implementation
- [x] 1.1 Create `EventTypeGroup` model and update `EventType` relationship in `backend/booking/models.py`.
- [x] 1.2 Generate and apply Django migrations.
- [x] 1.3 Create a data migration script to initialize groups and assign existing types.
- [x] 1.4 Update `EventTypeSerializer` in `backend/booking/serializers.py` to include `group_id`.
- [x] 1.5 Register `EventTypeGroup` in `backend/booking/admin.py` and update `EventTypeAdmin`.

## 2. Frontend Implementation
- [x] 2.1 Update types and store in `booking/src/store/useBookingStore.ts` to include `lockedGroupId`.
- [x] 2.2 Update `fetchServices` in `booking/src/lib/api/endpoints/services.ts` to handle the new `group_id` field.
- [x] 2.3 Implement group detection logic in `booking/src/components/organisms/BookingFlow.tsx`.
- [x] 2.4 Apply filtering logic in `booking/src/components/organisms/BookingServiceSelection.tsx`.

## 3. Validation
- [x] 3.1 Verify that `?service=6` (Course) locks the UI to the "Courses" group.
- [x] 3.2 Verify that removing the service does not unlock the group.
- [x] 3.3 Verify that no URL parameters show all service categories.
