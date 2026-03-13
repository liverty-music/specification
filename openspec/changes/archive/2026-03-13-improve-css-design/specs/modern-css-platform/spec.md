## ADDED Requirements

### Requirement: CSS `@layer` for cascade management
All CSS styles SHALL be organized into explicit `@layer` blocks following the CUBE CSS methodology. The cascade order SHALL be enforced by a single `@layer` declaration in the CSS entry point.

#### Scenario: Layer declaration establishes cascade
- **WHEN** `src/styles/main.css` is parsed
- **THEN** the `@layer` declaration SHALL establish the order: `reset, tokens, global, composition, utility, block, exception`
- **AND** all CSS files SHALL place their rules inside the appropriate layer
- **AND** the `cube/require-layer` stylelint rule SHALL report zero warnings across all files

#### Scenario: Layer order prevents specificity wars
- **WHEN** a block-layer rule and a utility-layer rule target the same element
- **THEN** the block-layer rule SHALL win due to its later position in the cascade order
- **AND** no `!important` SHALL be needed to resolve layer conflicts

---

### Requirement: CSS `@scope` for component isolation
Component-specific styles in the block layer SHALL use `@scope()` to prevent style leakage beyond component boundaries.

#### Scenario: Component CSS scoped to custom element
- **WHEN** a component CSS file defines styles (e.g., `event-card.css`)
- **THEN** all rules SHALL be inside `@layer block { @scope(event-card) { ... } }`
- **AND** selectors within the scope SHALL only match descendants of the `<event-card>` element
- **AND** the `cube/block-require-scope` stylelint rule SHALL report zero warnings

#### Scenario: Scope limit prevents deep leaking
- **WHEN** a scoped component contains nested components
- **THEN** the parent scope's styles SHALL NOT affect elements inside child component boundaries
- **AND** `@scope(<parent>) to (<child>)` syntax MAY be used when explicit scope limits are needed

---

### Requirement: No viewport media queries for component responsiveness
Components SHALL use CSS Container Queries for responsive layout, not viewport-based media queries. Viewport media queries SHALL only be used for truly viewport-dependent concerns (e.g., `prefers-reduced-motion`, `prefers-color-scheme`).

#### Scenario: Component layout uses container queries
- **WHEN** a component needs to adapt its layout to available space
- **THEN** the component SHALL use `@container` rules, not `@media (min-width: ...)` or `@media (max-width: ...)`
- **AND** the stylelint configuration SHALL warn on viewport-width media queries in component CSS

## MODIFIED Requirements

### Requirement: OKLCH color enforcement
All color definitions in CSS SHALL use the `oklch()` function. Legacy color functions and hex notation SHALL be rejected by Stylelint.

#### Scenario: OKLCH used for solid colors
- **WHEN** a CSS property requires a color value (e.g., `color`, `background-color`, `border-color`)
- **THEN** the value SHALL use `oklch()` notation
- **AND** Stylelint SHALL reject `rgb()`, `rgba()`, `hsl()`, `hsla()`, and hex colors

#### Scenario: OKLCH used for transparency
- **WHEN** a color requires an alpha/transparency component
- **THEN** the value SHALL use `oklch(L C H / alpha)` syntax
- **AND** legacy `rgba(R G B / alpha)` SHALL be rejected

#### Scenario: Color derivation uses color-mix()
- **WHEN** a color needs to be derived from a base token (e.g., hover state, transparency variant)
- **THEN** the value SHALL use `color-mix(in oklch, ...)` instead of defining a separate token
- **AND** the `cube/prefer-color-mix` stylelint rule SHALL report zero warnings

## REMOVED Requirements

### Requirement: Tailwind theme colors exempt
**Reason**: TailwindCSS is being removed from the project. The `theme()` function and Tailwind-generated CSS custom properties will no longer exist.
**Migration**: All color values are now plain CSS custom properties in `tokens.css`, referenced via `var(--color-*)`. The OKLCH enforcement applies universally — no exemptions needed.
