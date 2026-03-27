## MODIFIED Requirements

### Requirement: Dashboard Help Content — Lane Stage Colors

The dashboard help content SHALL display lane stage labels with color-coded text matching the stage colors. Stage-color identification SHALL use CSS class selectors scoped to the `page-help` block, not `data-stage` attributes, to avoid selector collisions with `concert-highway` stage headers.

#### Scenario: Stage labels render with correct colors via CSS classes

- **WHEN** the dashboard help content is displayed
- **THEN** the HOME stage label SHALL use `color: var(--color-stage-home)` via the `.stage-home` class
- **AND** the NEAR stage label SHALL use `color: var(--color-stage-near)` via the `.stage-near` class
- **AND** the AWAY stage label SHALL use `color: var(--color-stage-away)` via the `.stage-away` class

#### Scenario: Page-help labels do not collide with concert-highway selectors

- **WHEN** `document.querySelector('[data-stage="home"]')` is called from any component
- **THEN** the query SHALL NOT match any element inside the `page-help` component
- **AND** page-help stage labels SHALL use CSS classes (e.g., `stage-home`) instead of `data-stage` attributes

## ADDED Requirements

### Requirement: Top-layer Popover Text Color Inheritance

All popover and dialog elements promoted to the browser's top-layer SHALL inherit the application's text color. The global CSS layer SHALL set `color: var(--color-text-primary)` on `:where([popover], dialog)` to prevent top-layer elements from inheriting the browser-default `color: black` from `<html>`.

#### Scenario: Bottom-sheet text is readable on dark background

- **WHEN** a `bottom-sheet` component opens as a popover in the top-layer
- **THEN** all text inside the bottom-sheet SHALL inherit `color: var(--color-text-primary)` (near-white)
- **AND** the text SHALL be readable against the dark sheet background (`var(--color-surface-overlay)`)

#### Scenario: Global rule uses zero specificity

- **WHEN** the global CSS sets `color` on popover/dialog elements
- **THEN** the rule SHALL use `:where()` pseudo-class for zero specificity
- **AND** any block-level CSS rule SHALL be able to override the color without specificity conflicts
