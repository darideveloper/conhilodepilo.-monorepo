# Design: Landing Page Branding

## Architectural Overview
The landing pages `/success` and `/cancel` currently use a centered card layout. We will replace the status icon circle with the brand logo as an `img` tag at the top of the card's content, maintaining the existing aesthetics while improving brand consistency.

## Component Selection
We will use the existing `/logo.webp` asset available in the `landing/public/` directory.

## Layout Details
The logo will be centered within the card, replacing the old status circle.
- Height: `h-16` (64px)
- Margin Bottom: `mb-4`
- Object fit: `contain`
