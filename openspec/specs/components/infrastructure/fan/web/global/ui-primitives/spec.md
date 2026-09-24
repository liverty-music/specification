# UI Primitives

## Purpose

The small shared building blocks every screen uses: the loading spinner, icons, and the placeholder shown for empty, loading and error states.

## Requirements

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

### Requirement: SVG Icon Component
The system SHALL provide a centralized `<svg-icon>` custom element as the single source of truth for all SVG icon definitions, eliminating inline SVG duplication across templates.

#### Scenario: Icon rendering by name
- **WHEN** `<svg-icon name="home">` is rendered
- **THEN** the component SHALL display the SVG icon matching the given name
- **AND** only the matched icon SHALL be present in the DOM (via Aurelia `switch.bind`)
- **AND** unrecognized names SHALL render nothing (default-case fallback)

#### Scenario: Size variants
- **WHEN** `<svg-icon>` is rendered with a `size` attribute
- **THEN** the host element SHALL set `data-size` to the given value
- **AND** the component SHALL support sizes: xs (0.75rem), sm (1rem), md (1.25rem), lg (1.5rem), xl (2.5rem)
- **AND** the default size SHALL be md when no size is specified

#### Scenario: Icon set coverage
- **WHEN** the icon component is registered
- **THEN** it SHALL include at minimum these icons: home, search, discover, music, my-artists, ticket, tickets, settings, check, alert-triangle, warning, info, x-circle, x, chevron-right, arrow-left, trash, plus, map-pin, calendar, link, clock, globe, bell, lock, qr-code, list, grid

#### Scenario: Color inheritance
- **WHEN** `<svg-icon>` is placed inside a colored container
- **THEN** stroke-based icons SHALL use `stroke="currentColor"` to inherit the parent's text color
- **AND** fill-based icons (warning, x-circle) SHALL use `fill="currentColor"`

---

### Requirement: State Placeholder Component
The system SHALL provide a `<state-placeholder>` custom element for displaying empty, error, and informational states with a consistent centered layout.

#### Scenario: Rendering with icon only
- **WHEN** `<state-placeholder icon="music">` is rendered with slotted content
- **THEN** the component SHALL display an xl-sized svg-icon
- **AND** the slotted content SHALL be projected via `<au-slot>` below the icon
- **AND** the content SHALL be vertically and horizontally centered

#### Scenario: No icon
- **WHEN** `<state-placeholder>` is rendered without an `icon` attribute
- **THEN** no svg-icon SHALL be rendered
- **AND** only the slotted content SHALL be displayed

#### Scenario: Custom content via slot
- **WHEN** child content is placed inside `<state-placeholder>`
- **THEN** the content SHALL be projected via `<au-slot>`
- **AND** this SHALL allow pages to provide titles, descriptions, buttons, links, or `<loading-spinner>` elements

---
