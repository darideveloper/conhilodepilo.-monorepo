# Limit Course Card Description

## Why
Currently, the `CourseCard` component (`landing/src/components/molecules/CourseCard.astro`) displays the parsed markdown description without any length constraints. Long descriptions can break the uniformity of the cards layout on the home page. Attempting to truncate the string before parsing it into Markdown can result in broken HTML tags or invalid Markdown formatting.

## Summary
Limit the maximum number of characters rendered in the description of the `CourseCard` on the landing page's home. The truncation must happen via CSS to prevent breaking the Markdown formatting or HTML tags.

## Proposed Solution
Use Tailwind CSS's `line-clamp` utility on the wrapper element that renders the Markdown. Applying `line-clamp-3` will visually truncate the content after three lines, displaying an ellipsis (`...`) without affecting the underlying DOM structure or breaking any HTML/Markdown.

## Impact
- **Frontend (Landing):** The Course Card description text will be constrained to a maximum of 3 lines.
- **Backend / APIs:** No change.
- **Data:** No change.

## Alternatives Considered
- Truncating the string via JavaScript/TypeScript before rendering. *Rejected* because truncating mid-Markdown can break tags and layout.
