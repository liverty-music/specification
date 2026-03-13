## REMOVED Requirements

### Requirement: Stylelint compatible with Tailwind CSS v4
**Reason**: TailwindCSS was removed from the project in `improve-css-design`. The CUBE CSS architecture uses plain `@layer`, `@scope`, and CSS custom properties — no Tailwind directives exist in the codebase.
**Migration**: Remove `@theme` from `ignoreAtRules` and `theme()` from `ignoreFunctions` in `stylelint.config.js`. No CSS file changes needed as no Tailwind directives remain.

## ADDED Requirements

### Requirement: Stylelint enforces stacking context management
The linter SHALL disallow `z-index` without escape hatches. Components SHALL manage stacking via `isolation: isolate` on parent containers instead of arbitrary z-index values.

#### Scenario: No stylelint-disable for z-index
- **WHEN** stylelint runs against all CSS files
- **THEN** zero `stylelint-disable` comments for the `property-disallowed-list` rule SHALL exist
- **AND** all stacking requirements SHALL be resolved via `isolation: isolate` or natural stacking contexts

### Requirement: Stylelint enforces accessibility media queries
The linter SHALL not flag accessibility-related media features as errors.

#### Scenario: prefers-contrast allowed
- **WHEN** a CSS file contains `@media (prefers-contrast: more)` or `@media (prefers-contrast: less)`
- **THEN** Stylelint SHALL not report any errors

#### Scenario: forced-colors allowed
- **WHEN** a CSS file contains `@media (forced-colors: active)`
- **THEN** Stylelint SHALL not report any errors

#### Scenario: prefers-reduced-motion allowed
- **WHEN** a CSS file contains `@media (prefers-reduced-motion: reduce)`
- **THEN** Stylelint SHALL not report any errors
