## CHANGED Requirements

### Requirement: Tooltip Visual Treatment (CHANGED)

The coach mark tooltip SHALL render with a transparent background, allowing the handwritten text to float directly on the dark overlay.

#### Scenario: Tooltip renders without solid background
- **WHEN** the coach mark tooltip is displayed
- **THEN** `.coach-mark-tooltip` SHALL have `background: transparent`
- **AND** `.coach-mark-tooltip` SHALL have `filter: none` (no drop-shadow)
- **AND** the tooltip text color SHALL remain `var(--color-white)`
- **AND** the font SHALL remain `var(--coach-font-handwritten)` ("Klee One", cursive)
- **AND** the tooltip SHALL be visually readable against the 70% black overlay
