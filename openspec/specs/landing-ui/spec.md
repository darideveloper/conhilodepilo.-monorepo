# landing-ui Specification

## Purpose
TBD - created by archiving change limit-coursecard-description. Update Purpose after archive.
## Requirements
### Requirement: Course Card Description Limitation
The Course Card component on the Landing page MUST limit its displayed description to a maximum of 3 lines to maintain layout consistency. The truncation MUST be applied visually (e.g., using CSS line-clamp) to ensure that any underlying Markdown or HTML structures remain intact and are not broken mid-tag.

#### Scenario: Rendering a long markdown description
- **Given** a Course Card with a markdown description that renders to more than 3 lines of text
- **When** the card is displayed on the frontend
- **Then** the text should be truncated at the end of the third line with an ellipsis (`...`)
- **And** no HTML elements should be left unclosed or broken due to the truncation

