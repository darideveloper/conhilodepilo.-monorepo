# Spec: Landing Gallery Assets

## ADDED Requirements

### Requirement: Use optimized gallery images
The landing page gallery MUST use optimized `.webp` images to improve performance.

#### Scenario: Display new gallery images
- **Given** the user provides new `.webp` images
- **When** the images are placed in `landing/src/assets/images/gallery/`
- **And** `Gallery.astro` is updated to import them
- **Then** the gallery should display the new images without broken links
