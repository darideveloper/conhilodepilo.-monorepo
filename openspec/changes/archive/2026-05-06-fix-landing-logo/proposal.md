# Proposal: Add Brand Logo to Success and Cancel Pages

## Why
The `/success` and `/cancel` pages in the landing application were missing the brand logo, and the generic status icon (circle with a check or X) felt disconnected from the brand identity. Replacing the status icon with the brand logo provides a cleaner, more professional look and ensures users immediately recognize the brand after being redirected from external services like Stripe.

## What Changes
- `landing/src/pages/success.astro`: Removed the status icon circle and added the brand logo.
- `landing/src/pages/cancel.astro`: Removed the status icon circle and added the brand logo.
- Spec Delta: Added branding requirements to the `landing-ui` specification.

## Proposed Solution
Introduce the brand logo on the `/success` and `/cancel` pages. The logo will be placed prominently within the feedback card, replacing the generic status icon circle. This ensures users immediately recognize the brand and provides a cleaner, more professional look.

## Scope
- `landing/src/pages/success.astro`
- `landing/src/pages/cancel.astro`

## Impact
- **Branding**: Improved brand consistency across the payment flow.
- **UX**: Clearer context for users returning from Stripe.
