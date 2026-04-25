# Spec Delta: Backend Models for Service Grouping

## ADDED Requirements
### Requirement: Service Categorization
The system MUST allow grouping service categories (Event Types) into broader groups to facilitate filtering and specialization of the booking flow.

#### Scenario: Assign Group to Event Type
- **Given** an existing `EventType` "Depilación con hilo".
- **And** a group "Salon Services" with ID 1.
- **When** the admin assigns "Salon Services" to "Depilación con hilo".
- **Then** the API MUST return `group_id: 1` for that event type.
