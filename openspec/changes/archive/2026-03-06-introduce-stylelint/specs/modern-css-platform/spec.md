## MODIFIED Requirements

### Requirement: CSS Logical Properties
Layout, spacing, and positioning properties SHALL use CSS Logical Properties for internationalization readiness. Compliance SHALL be enforced by Stylelint via `property-disallowed-list`.

#### Scenario: Margin and padding use logical properties
- **WHEN** a CSS file contains margin or padding declarations
- **THEN** the declarations SHALL use `margin-inline`, `margin-block`, `padding-inline`, `padding-block` (or their `-start`/`-end` longhands) instead of physical `margin-left`, `margin-top`, etc.
- **AND** Stylelint SHALL reject physical margin/padding properties as errors

#### Scenario: Border and positioning use logical properties
- **WHEN** a CSS file contains border or positioning declarations
- **THEN** the declarations SHALL use `border-inline-start`, `inset-inline`, `inset-block-end`, etc. instead of physical equivalents
- **AND** Stylelint SHALL reject physical border/positioning properties as errors

#### Scenario: All existing physical properties migrated
- **WHEN** the Stylelint configuration is applied to the codebase
- **THEN** all existing physical directional properties SHALL have been migrated to logical equivalents
- **AND** `stylelint --fix` or manual migration SHALL have resolved all violations

## ADDED Requirements

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

#### Scenario: Tailwind theme colors exempt
- **WHEN** a color value is provided via Tailwind `theme()` function or CSS custom properties (e.g., `var(--color-brand-primary)`)
- **THEN** the value SHALL not be subject to color function linting
