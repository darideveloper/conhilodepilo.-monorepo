# landing-ui-components Specification Delta

## MODIFIED Requirements

### Requirement: Header navigation links MUST use absolute paths
The main navigation links and primary call-to-action (CTA) buttons in the Header component MUST use absolute root paths (e.g., `/#section-id`) rather than relative hash links (e.g., `#section-id`) to ensure they function correctly from any subpage.

#### Scenario: Navigating from a subpage
- **Given** a user is on a subpage
- **When** they click a navigation link or the "Reserva Ahora" CTA button in the Header
- **Then** they are correctly redirected to the homepage and scrolled to the respective section (e.g., `/#servicios`).
