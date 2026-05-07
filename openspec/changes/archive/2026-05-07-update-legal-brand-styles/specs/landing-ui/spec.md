## ADDED Requirements

### Requirement: Brand Text Highlighting
The landing site SHALL use the brand's primary color for bold text highlights to reinforce visual identity.

#### Scenario: Bold text in content
- **GIVEN** any component or MDX content using `<strong>` or `**bold**`
- **THEN** the text SHALL be rendered in the `brand-primary` color
- **AND** have a bold font weight.
