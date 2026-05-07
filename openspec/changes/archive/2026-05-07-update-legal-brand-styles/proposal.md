# Change: Update Legal Brand Styles

## Why
The legal pages were previously using a dark theme (`prose-invert`) that was inconsistent with the light background of the landing site. Additionally, bold text was white, which was hard to read and didn't reflect the brand identity. This change aligns the legal pages and global text highlights with the brand's primary color palette.

## What Changes
- Removed `prose-invert` from legal page rendering to support the light theme.
- Updated legal page text and heading colors to use UI text defaults.
- **MODIFIED** bold text (`strong`) across the entire landing site to use the brand's primary color instead of white/default.
- Updated horizontal rules in legal pages for better visibility on light backgrounds.

## Impact
- Affected specs: `legal-pages`, `landing-ui`
- Affected code: `landing/src/pages/legal/[slug].astro`, `landing/src/styles/global.css`
