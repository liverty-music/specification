## ADDED Requirements

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

### Requirement: Stylelint compatible with Tailwind CSS v4
The linter SHALL not flag valid Tailwind v4 directives or modern CSS at-rules as errors.

#### Scenario: Tailwind at-rules accepted
- **WHEN** a CSS file contains `@theme`, `@layer`, or `@apply` directives
- **THEN** Stylelint SHALL not report unknown at-rule errors

#### Scenario: Modern CSS at-rules accepted
- **WHEN** a CSS file contains `@container`, `@starting-style`, or `@property` at-rules
- **THEN** Stylelint SHALL not report unknown at-rule errors

#### Scenario: Tailwind theme function accepted
- **WHEN** a CSS file uses the `theme()` function
- **THEN** Stylelint SHALL not report unknown function errors

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
