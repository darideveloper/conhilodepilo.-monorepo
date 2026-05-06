# Proposal: Update "Reserva Ahora" CTA Link

## Problem
The "Reserva Ahora" button in the header currently has a placeholder link (`href="#"`), which doesn't lead the user to any functional part of the site.

## Proposed Change
Update the "Reserva Ahora" button in the `Header.astro` component to link to the services section (`/#servicios`). This ensures that:
1. If the user is on the homepage, the page scrolls down to the services.
2. If the user is on another page, they are redirected to the homepage and then scrolled to the services.

This change applies to both the mobile navigation button and the desktop header button.

## Impact
- **UX**: Provides a clear path for users wanting to book or see services.
- **Consistency**: Aligns the CTA with other navigation links that use absolute root paths.
