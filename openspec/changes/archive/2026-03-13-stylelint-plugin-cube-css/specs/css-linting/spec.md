## MODIFIED Requirements

### Requirement: Stylelint compatible with Tailwind CSS v4
The linter SHALL not flag valid Tailwind v4 directives, modern CSS at-rules, or CUBE CSS plugin rules as errors.

#### Scenario: Tailwind at-rules accepted
- **WHEN** a CSS file contains `@theme`, `@layer`, or `@apply` directives
- **THEN** Stylelint SHALL not report unknown at-rule errors

#### Scenario: Modern CSS at-rules accepted
- **WHEN** a CSS file contains `@container`, `@starting-style`, `@property`, or `@scope` at-rules
- **THEN** Stylelint SHALL not report unknown at-rule errors

#### Scenario: Tailwind theme function accepted
- **WHEN** a CSS file uses the `theme()` function
- **THEN** Stylelint SHALL not report unknown function errors

#### Scenario: CUBE CSS plugin rules configured
- **WHEN** `stylelint.config.js` is loaded
- **THEN** the `stylelint-plugin-cube-css` plugin SHALL be registered
- **AND** all 14 `cube/*` rules SHALL be configured
