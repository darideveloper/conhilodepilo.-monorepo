# Design: Service Grouping & Filtering

## Data Model
`EventTypeGroup` is a simple classification model.
- `id`: Auto-incrementing integer (used for filtering).
- `name`: Human-readable name (e.g., "Courses").

`EventType` (Service Category) links to a group:
- `group`: ForeignKey to `EventTypeGroup` (nullable for legacy/unclassified types).

## Filtering Strategy
1. **Identification:** `BookingFlow` detects the `service` ID from the URL.
2. **Lookup:** It finds the category belonging to that service and retrieves its `group_id`.
3. **Locking:** `lockedGroupId` is set in the Zustand store.
4. **Rendering:** `BookingServiceSelection` computes `filteredServicesData = servicesData.filter(cat => !lockedGroupId || cat.group_id === lockedGroupId)`.

## Migration Strategy (Assume based on name)
- **Salon Services**: "Depilación con hilo", "Depilación con Cera Desechable", "Tratamientos Especiales".
- **Courses**: "Cursos de formación 100% profesional".

## User Experience
- If a user enters via a general booking link, they see all categories.
- If they enter via a specific course link, the UI "specializes" for courses, preventing confusion with salon services.
