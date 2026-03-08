## MODIFIED Requirements

### Requirement: CSS Logical Properties
Layout, spacing, and positioning properties SHALL use CSS Logical Properties for internationalization readiness. Compliance SHALL be enforced by Stylelint via `property-disallowed-list` for CSS files. Tailwind HTML templates SHALL use logical utility classes exclusively.

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

#### Scenario: Tailwind templates use logical utility classes
- **WHEN** an HTML template uses Tailwind utility classes for margin, padding, or positioning
- **THEN** the template SHALL use logical equivalents: `ms-*`/`me-*` instead of `ml-*`/`mr-*`, `ps-*`/`pe-*` instead of `pl-*`/`pr-*`, `start-*`/`end-*` instead of `left-*`/`right-*`
- **AND** physical directional Tailwind classes SHALL NOT appear in HTML templates

## ADDED Requirements

### Requirement: Dynamic Viewport Height
Viewport-height declarations SHALL use `100dvh` (dynamic viewport height) instead of `100vh` to correctly adapt to mobile browser chrome changes.

#### Scenario: CSS files use dvh units
- **WHEN** a CSS file requires full viewport height
- **THEN** the declaration SHALL use `100dvh` instead of `100vh`
- **AND** `100vh` SHALL NOT appear in any CSS file

#### Scenario: Tailwind templates use dvh utilities
- **WHEN** an HTML template requires full viewport height via Tailwind
- **THEN** the template SHALL use `h-dvh` instead of `h-screen`
