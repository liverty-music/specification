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
