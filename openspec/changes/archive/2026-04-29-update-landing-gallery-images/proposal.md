# Proposal: Update Landing Gallery Images

## Problem
The current gallery images in the landing page are using older `.jpg` files and need to be replaced with new, optimized `.webp` images provided by the user.

## Proposed Solution
Replace the existing 8 gallery images in `landing/src/assets/images/gallery/` with the new versions from the local Downloads folder. The new images will be renamed to follow the existing naming convention (`gallery-01.webp`, `gallery-02.webp`, etc.) and the `Gallery.astro` component will be updated to reference these new files.

## Scope
-   `landing/src/assets/images/gallery/`: Remove old `.jpg` files and add new `.webp` files.
-   `landing/src/components/organisms/Gallery.astro`: Update imports and references.

## Non-goals
-   Changing the gallery layout or logic.
-   Updating other images outside the gallery.
