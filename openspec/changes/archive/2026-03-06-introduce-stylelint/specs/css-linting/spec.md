## ADDED Requirements

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

