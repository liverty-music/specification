## MODIFIED Requirements

### Requirement: Tooltip Anchor Positioning

The coach mark tooltip SHALL be positioned using CSS Anchor Positioning relative to the target element. The tooltip SHALL use `position-area: block-end inline-start` to bias placement below and to the inline-start side of the target. This inline bias enables `flip-inline` detection via anchored container queries.

#### Scenario: Tooltip appears below target with inline-start bias

- **WHEN** the coach mark is active
- **THEN** the tooltip SHALL use `position-anchor` referencing the target's anchor name
- **AND** the tooltip SHALL use `position-area: block-end inline-start` as the default placement
- **AND** the tooltip SHALL use `position-try-fallbacks: flip-block, flip-inline, flip-block flip-inline` for overflow handling in both axes

#### Scenario: Tooltip flips inline when viewport constrains

- **WHEN** the tooltip at `inline-start` would overflow the viewport's inline-start edge
- **THEN** the browser SHALL apply the `flip-inline` fallback, placing the tooltip at `block-end inline-end`
- **AND** the `@container anchored (fallback: flip-inline)` query SHALL match on the tooltip container

### Requirement: Inline SVG Directional Arrow

The tooltip SHALL include a hand-drawn style directional arrow rendered as inline SVG. No external image assets (`<img>`, `.png`, `.svg` files) SHALL be used. The arrow SHALL visually connect the tooltip to the spotlight target by curving toward the target's position.

#### Scenario: Arrow direction adapts to 4-state tooltip placement

- **WHEN** the tooltip is below-left of the target (default `block-end inline-start`)
- **THEN** the `coach-arrow-above` SVG SHALL be visible with `transform: scaleX(-1)` (curving right toward target)
- **AND** the `coach-arrow-below` SVG SHALL be hidden
- **WHEN** the tooltip is below-right of the target (fallback `flip-inline`)
- **THEN** the `coach-arrow-above` SVG SHALL be visible with `transform: scaleX(1)` (curving left toward target)
- **AND** the `coach-arrow-below` SVG SHALL be hidden
- **WHEN** the tooltip is above-left of the target (fallback `flip-block`)
- **THEN** the `coach-arrow-below` SVG SHALL be visible with `transform: scaleX(-1)` (curving right toward target)
- **AND** the `coach-arrow-above` SVG SHALL be hidden
- **WHEN** the tooltip is above-right of the target (fallback `flip-block flip-inline`)
- **THEN** the `coach-arrow-below` SVG SHALL be visible with `transform: scaleX(1)` (curving left toward target)
- **AND** the `coach-arrow-above` SVG SHALL be hidden

#### Scenario: Arrow mirroring uses CSS transform only

- **WHEN** the arrow direction changes due to inline flipping
- **THEN** the mirroring SHALL be achieved via CSS `transform: scaleX(-1)` on the existing SVG elements
- **AND** no additional SVG path variants SHALL be required
- **AND** no JavaScript SHALL be used to determine arrow direction

#### Scenario: Arrow drawing animation on appearance

- **WHEN** the tooltip first appears or the target changes
- **THEN** the arrow path SHALL animate with a drawing effect using `stroke-dasharray` / `stroke-dashoffset` over approximately 600ms
- **AND** the arrowhead SHALL fade in after the line drawing completes (300ms delay)

#### Scenario: Arrow inherits theme color

- **WHEN** the tooltip is rendered
- **THEN** the SVG SHALL use `stroke="currentColor"` to inherit the tooltip's text color
- **AND** the arrow SHALL automatically adapt to theme changes without separate assets

#### Scenario: Arrow with reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the drawing animation SHALL be disabled (arrow appears immediately)
- **AND** the arrow SHALL still be visible in its final drawn state
- **AND** the `transform: scaleX()` mirroring SHALL still apply (it is a layout property, not an animation)

## Test Cases

### Unit Tests (Vitest — coach-mark.spec.ts)

#### TC-ARROW-01: Default state shows above-arrow mirrored

- **Given** a coach mark is active with tooltip below-left of target
- **When** no position-try fallback is applied
- **Then** `coach-arrow-above` SHALL be visible
- **And** `coach-arrow-above` SHALL have `transform: scaleX(-1)`
- **And** `coach-arrow-below` SHALL be hidden

#### TC-ARROW-02: flip-inline shows above-arrow unmirrored

- **Given** a coach mark is active with tooltip below-right of target
- **When** the `flip-inline` fallback is applied
- **Then** `coach-arrow-above` SHALL be visible with `transform: scaleX(1)`

#### TC-ARROW-03: flip-block shows below-arrow mirrored

- **Given** a coach mark is active with tooltip above-left of target
- **When** the `flip-block` fallback is applied
- **Then** `coach-arrow-below` SHALL be visible with `transform: scaleX(-1)`
- **And** `coach-arrow-above` SHALL be hidden

#### TC-ARROW-04: flip-block flip-inline shows below-arrow unmirrored

- **Given** a coach mark is active with tooltip above-right of target
- **When** the `flip-block flip-inline` fallback is applied
- **Then** `coach-arrow-below` SHALL be visible with `transform: scaleX(1)`
- **And** `coach-arrow-above` SHALL be hidden

### E2E Tests (Playwright — visual verification)

#### TC-ARROW-E2E-01: Arrow points toward right-aligned target

- Navigate to dashboard with coach mark targeting a right-aligned concert card
- Verify the arrow curves to the right (toward the card), not to the left
