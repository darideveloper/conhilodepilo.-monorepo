## Context
The landing site uses a light theme defined in `global.css` (`bg-ui-bg-light`). The legal pages (Privacy Policy, Terms of Service) are rendered from MDX content using Tailwind's typography plugin (`prose`).

## Goals
- Ensure legal pages are readable on a light background.
- Incorporate brand colors into text elements for better visual identity.
- Centralize styling for bold text to ensure consistency across the site.

## Decisions
- **Global `strong` styling**: Added `strong { color: var(--color-brand-primary); font-weight: 700; }` to `global.css`. This ensures that any `**bold text**` in MDX or `<strong>` tags in components automatically inherits the brand's primary color.
- **Removal of `prose-invert`**: The `prose-invert` class is designed for dark backgrounds. Since the site is light, removing it allows the default `prose` styles to apply, which we then further customize for brand alignment.
- **Local Prose Customization**: In `[slug].astro`, we override specific `prose` elements (h1, h2, p, ul, strong, hr) using `@apply` to ensure they match the UI design tokens (`text-ui-text-main`, `text-brand-primary`, etc.).

## Risks / Trade-offs
- **Contrast**: The brand primary color (`#f3c6bf`) is relatively light. We must ensure it has sufficient contrast against the light background (`#FFF9F6`). While it serves as a brand highlight, critical information should not rely solely on color if contrast is borderline.

## Migration Plan
- This is a styling-only change and does not require data migration. It was applied directly to the Astro templates and global CSS.
