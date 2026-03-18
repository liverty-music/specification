## ADDED Requirements

### Requirement: Loading Spinner Custom Element
The system SHALL provide a `<loading-spinner>` custom element as a visual primitive for animated loading indicators with size variants.

#### Scenario: Default rendering
- **WHEN** `<loading-spinner>` is rendered without attributes
- **THEN** the CE SHALL display a circular spinner with `md` size (2rem)
- **AND** the spinner SHALL use a border-based animation: solid border with one transparent side
- **AND** the border color SHALL derive from `var(--color-brand-accent)` at 30% opacity with `border-block-start-color` at full opacity
- **AND** `animation: spin 0.8s linear infinite` SHALL be applied

#### Scenario: Size variants
- **WHEN** `<loading-spinner size="sm">` is rendered
- **THEN** the spinner SHALL be 1rem with 1.5px border
- **WHEN** `<loading-spinner size="md">` is rendered
- **THEN** the spinner SHALL be 2rem with 2px border
- **WHEN** `<loading-spinner size="lg">` is rendered
- **THEN** the spinner SHALL be 2.5rem with 3px border

#### Scenario: Accessibility semantics
- **WHEN** the spinner is rendered
- **THEN** the host element SHALL be an `<output>` with `role="status"` and `aria-busy="true"`

#### Scenario: Color inheritance
- **WHEN** the spinner is placed inside a container with custom `--color-brand-accent`
- **THEN** the spinner border color SHALL inherit from that custom property

#### Scenario: Reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** the spin animation SHALL be paused or removed

#### Scenario: CUBE CSS layer
- **WHEN** the spinner CSS is loaded
- **THEN** all styles SHALL be defined within `@layer block` using `@scope (loading-spinner)`
