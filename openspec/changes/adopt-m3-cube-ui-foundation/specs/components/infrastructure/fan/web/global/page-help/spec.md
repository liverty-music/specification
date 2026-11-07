## MODIFIED Requirements

### Requirement: Help sheet visual readability

The help bottom-sheet SHALL use design tokens that ensure clear visual distinction from the app surface.

#### Scenario: Sheet background, title font, and muted text rendering

- **WHEN** the help bottom-sheet is displayed
- **THEN** the sheet background SHALL use the `surface-container-high` color role so the sheet is visually elevated above the page surface
- **AND** help section titles SHALL use a headline style, so they are in the brand typeface
- **AND** secondary text (notes, tips) SHALL use the `on-surface-variant` color role instead of reduced opacity
