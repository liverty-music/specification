## MODIFIED Requirements

### Requirement: Tooltip Anchor Positioning

The coach mark tooltip SHALL be positioned using CSS Anchor Positioning relative to the target element.

#### Scenario: Tooltip appears below target

- **WHEN** the coach mark is active
- **THEN** the tooltip SHALL use `position-anchor` referencing the target's anchor name
- **AND** the tooltip SHALL use `position-area: block-end` as the default placement
- **AND** the tooltip SHALL use `position-try-fallbacks: flip-block` for overflow handling
- **AND** the tooltip SHALL define `anchor-name: --coach-tooltip` so pseudo-elements can reference its edges

### Requirement: Inline SVG Directional Arrow

The tooltip SHALL include a symmetric triangular arrow rendered as a CSS `::before` pseudo-element with `clip-path: polygon()`. No SVG elements, external image assets, or JavaScript SHALL be used for the arrow. The arrow SHALL visually connect the tooltip to the spotlight target and automatically orient toward the target when the tooltip position flips.

#### Scenario: Arrow direction adapts to tooltip placement

- **WHEN** the tooltip is positioned below the target (`position-area: block-end`)
- **THEN** the `::before` pseudo-element SHALL render a triangular arrow pointing upward toward the target
- **WHEN** the tooltip is positioned above the target (via `position-try-fallbacks: flip-block`)
- **THEN** the same `::before` pseudo-element SHALL render a triangular arrow pointing downward toward the target
- **AND** the direction change SHALL be handled via `margin: inherit` pattern — no `@container anchored` toggling or display switching SHALL be needed

#### Scenario: Arrow is horizontally centered on target

- **WHEN** the tooltip arrow is rendered
- **THEN** the arrow SHALL be horizontally centered on the target element via `left: calc(anchor(--coach-target center) - var(--arrow-size) / 2)`
- **AND** the arrow center SHALL be within one arrow-width of the target's horizontal center

#### Scenario: Arrow is positioned between tooltip and target

- **WHEN** the tooltip is below the target
- **THEN** the arrow SHALL appear between the target's bottom edge and the tooltip's top edge
- **WHEN** the tooltip is above the target
- **THEN** the arrow SHALL appear between the tooltip's bottom edge and the target's top edge

#### Scenario: Arrow inherits theme color

- **WHEN** the tooltip is rendered
- **THEN** the `::before` pseudo-element SHALL use `background: inherit` to match the tooltip's background
- **AND** the arrow SHALL automatically adapt to theme changes

#### Scenario: Arrow with reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** any arrow appearance animation SHALL be disabled
- **AND** the arrow SHALL still be visible in its final state

## REMOVED Requirements

### Requirement: Inline SVG Directional Arrow (SVG implementation)

**Reason**: Replaced by CSS `::before` + `clip-path: polygon()` approach. SVG paths have asymmetric curves that cannot orient toward the target without JavaScript. The CSS pseudo-element approach uses a symmetric triangle that works natively with `flip-block`.

**Migration**: Remove `.coach-arrow-container`, `.coach-arrow-above`, `.coach-arrow-below` HTML elements and their CSS rules. The `::before` pseudo-element on `.coach-mark-tooltip` replaces all arrow functionality.
