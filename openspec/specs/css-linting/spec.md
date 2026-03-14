# CSS Linting

## Purpose

Defines the Stylelint configuration and rules that enforce modern CSS standards across the Liverty Music frontend. Works alongside Biome (which handles CSS formatting) to provide comprehensive CSS quality enforcement.

## Requirements

### Requirement: Stylelint enforces modern color functions
The linter SHALL disallow legacy color functions and hex notation, requiring OKLCH for all color definitions.

#### Scenario: Legacy rgb/rgba rejected
- **WHEN** a CSS file contains `rgb()`, `rgba()`, `hsl()`, or `hsla()` function calls
- **THEN** Stylelint SHALL report an error via the `function-disallowed-list` rule

#### Scenario: Hex colors rejected
- **WHEN** a CSS file contains a hex color value (e.g., `#fff`, `#4f46e5`)
- **THEN** Stylelint SHALL report an error via the `color-no-hex` rule

#### Scenario: OKLCH accepted
- **WHEN** a CSS file uses `oklch()` for color definitions
- **THEN** Stylelint SHALL not report any color-related errors

### Requirement: Stylelint enforces CSS Logical Properties
The linter SHALL disallow physical directional properties, requiring their logical equivalents.

#### Scenario: Physical margin/padding rejected
- **WHEN** a CSS file contains `margin-left`, `margin-right`, `margin-top`, `margin-bottom`, `padding-left`, `padding-right`, `padding-top`, or `padding-bottom`
- **THEN** Stylelint SHALL report an error via the `property-disallowed-list` rule

#### Scenario: Physical positional properties rejected
- **WHEN** a CSS file contains `top`, `right`, `bottom`, or `left` properties
- **THEN** Stylelint SHALL report an error via the `property-disallowed-list` rule

#### Scenario: Physical border properties rejected
- **WHEN** a CSS file contains `border-left`, `border-right`, `border-top`, `border-bottom` or their longhand variants (`-width`, `-style`, `-color`)
- **THEN** Stylelint SHALL report an error via the `property-disallowed-list` rule

#### Scenario: Logical equivalents accepted
- **WHEN** a CSS file uses `margin-inline-start`, `inset-block-end`, `padding-block`, `border-inline-start`, or `inset` shorthand
- **THEN** Stylelint SHALL not report any property errors

### Requirement: Stylelint enforces Container Queries over viewport-width media queries
The linter SHALL disallow width-based media features in `@media` rules to enforce `@container` usage for component-level responsiveness.

#### Scenario: Viewport-width media query rejected
- **WHEN** a CSS file contains `@media (width ...)`, `@media (min-width: ...)`, or `@media (max-width: ...)`
- **THEN** Stylelint SHALL report an error via the `media-feature-name-disallowed-list` rule

#### Scenario: Preference media queries allowed
- **WHEN** a CSS file contains `@media (prefers-reduced-motion: reduce)` or `@media (prefers-color-scheme: dark)`
- **THEN** Stylelint SHALL not report any errors

#### Scenario: Container queries allowed
- **WHEN** a CSS file uses `@container (min-width: ...)` or `@container (max-width: ...)`
- **THEN** Stylelint SHALL not report any errors

### Requirement: Stylelint prevents CSS anti-patterns
The linter SHALL disallow known anti-patterns that lead to maintainability issues.

#### Scenario: z-index rejected
- **WHEN** a CSS file contains a `z-index` declaration
- **THEN** Stylelint SHALL report an error via the `property-disallowed-list` rule

#### Scenario: !important rejected
- **WHEN** a CSS file contains `!important` in a declaration
- **THEN** Stylelint SHALL report an error via the `declaration-no-important` rule

#### Scenario: Float layout rejected
- **WHEN** a CSS file contains `float` or `clear` properties
- **THEN** Stylelint SHALL report an error via the `property-disallowed-list` rule

#### Scenario: ID selectors rejected
- **WHEN** a CSS file contains an ID selector (e.g., `#my-id`)
- **THEN** Stylelint SHALL report an error via the `selector-max-id` rule with a limit of 0

#### Scenario: Excessive specificity rejected
- **WHEN** a CSS selector exceeds specificity `0,4,0`
- **THEN** Stylelint SHALL report an error via the `selector-max-specificity` rule

#### Scenario: Deep selector nesting rejected
- **WHEN** a CSS selector exceeds 4 compound selectors
- **THEN** Stylelint SHALL report an error via the `selector-max-compound-selectors` rule

### Requirement: Stylelint enforces property declaration ordering
The linter SHALL enforce a consistent property declaration order grouped by function.

#### Scenario: Properties ordered by group
- **WHEN** a CSS declaration block is written
- **THEN** properties SHALL be ordered in the following group sequence: Interaction, Positioning, Layout, Box Model, Typography, Appearance, Transition/Animation
- **AND** `stylelint --fix` SHALL automatically reorder properties

### Requirement: Stylelint compatible with modern CSS at-rules
The linter SHALL not flag valid modern CSS at-rules or CUBE CSS plugin rules as errors.

#### Scenario: Standard CSS at-rules accepted
- **WHEN** a CSS file contains `@layer`, `@scope`, or `@property` at-rules
- **THEN** Stylelint SHALL not report unknown at-rule errors

#### Scenario: Modern CSS at-rules accepted
- **WHEN** a CSS file contains `@container`, `@starting-style`, `@property`, or `@scope` at-rules
- **THEN** Stylelint SHALL not report unknown at-rule errors

### Requirement: Stylelint enforces stacking context management
The linter SHALL disallow `z-index` via the `property-disallowed-list` rule. Components SHALL resolve stacking requirements through proper DOM structure — elements that need different stacking order SHALL NOT be placed as sticky siblings within the same scroll container. The `isolation: isolate` property MAY be used to scope stacking contexts where needed, but it does not substitute for correct DOM structure.

#### Scenario: No stylelint-disable for z-index
- **WHEN** stylelint runs against all CSS files
- **THEN** zero `stylelint-disable` comments for the `property-disallowed-list` rule SHALL exist
- **AND** all stacking requirements SHALL be resolved via proper DOM structure (e.g., moving fixed headers outside scroll containers)

#### Scenario: No magic numbers for sticky offsets
- **WHEN** a CSS file contains `position: sticky` with a non-zero `inset-block-start` value
- **THEN** the value SHALL reference a design token custom property
- **AND** hardcoded pixel values (e.g., `41px`) SHALL NOT be used

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

#### Scenario: CUBE CSS plugin rules configured
- **WHEN** `stylelint.config.js` is loaded
- **THEN** the `stylelint-plugin-cube-css` plugin SHALL be registered
- **AND** all 14 `cube/*` rules SHALL be configured

### Requirement: Stylelint integrated into CI pipeline
The linter SHALL run as part of the standard CI lint check.

#### Scenario: make lint runs Stylelint
- **WHEN** a developer runs `make lint`
- **THEN** Stylelint SHALL execute against all CSS files under `src/`
- **AND** lint failures SHALL cause a non-zero exit code

#### Scenario: make check gates commits
- **WHEN** a developer runs `make check` (pre-commit)
- **THEN** Stylelint SHALL execute as part of the check pipeline
- **AND** any Stylelint error SHALL block the commit
