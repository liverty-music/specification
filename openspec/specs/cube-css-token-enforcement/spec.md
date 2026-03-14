# cube-css-token-enforcement Specification

## Purpose

Enforces design token usage via `var()` references for spacing, color, typography, and animation properties in consumption layers (composition, utility, block, exception). Token definition layers (reset, tokens, global) are excluded.

## ADDED Requirements

### Requirement: `cube/require-token-variables` enforces `var()` for design token properties
Configured properties in consumption layers (composition, utility, block, exception) SHALL use `var()` references instead of raw literal values.

#### Scenario: `var()` value accepted
- **WHEN** `@layer block` contains `.card { padding: var(--space-m); }`
- **THEN** the rule SHALL not report an error

#### Scenario: Raw literal rejected
- **WHEN** `@layer block` contains `.card { padding: 16px; }`
- **THEN** the rule SHALL report an error: "Property 'padding' must use a design token via var()."

#### Scenario: Raw color rejected
- **WHEN** `@layer block` contains `.card { color: oklch(55% 0.25 260); }`
- **THEN** the rule SHALL report an error

#### Scenario: Raw font-size rejected
- **WHEN** `@layer utility` contains `.text-lg { font-size: 1.2rem; }`
- **THEN** the rule SHALL report an error

### Requirement: `calc()` expressions must contain at least one `var()`
When a token-enforced property uses `calc()`, the expression SHALL contain at least one `var()` reference.

#### Scenario: calc with var() accepted
- **WHEN** `@layer block` contains `.card { padding: calc(var(--space-m) - 1px); }`
- **THEN** the rule SHALL not report an error

#### Scenario: calc with division by literal accepted
- **WHEN** `@layer block` contains `.card { gap: calc(var(--space-s) / 2); }`
- **THEN** the rule SHALL not report an error

#### Scenario: Pure literal calc rejected
- **WHEN** `@layer block` contains `.card { padding: calc(16px + 4px); }`
- **THEN** the rule SHALL report an error: "Property 'padding': calc() must reference at least one design token via var()."

#### Scenario: Nested calc with var() accepted
- **WHEN** `@layer block` contains `.card { inline-size: calc(100% - var(--space-m) * 2); }`
- **THEN** the rule SHALL not report an error

### Requirement: Structural values bypass token enforcement
Values that are inherently structural (not design tokens) SHALL be allowed without `var()`.

#### Scenario: Zero accepted
- **WHEN** `@layer block` contains `.card { padding: 0; }`
- **THEN** the rule SHALL not report an error

#### Scenario: `auto` accepted
- **WHEN** `@layer block` contains `.card { margin-inline: auto; }`
- **THEN** the rule SHALL not report an error

#### Scenario: `none` accepted
- **WHEN** `@layer block` contains `.card { background: none; }`
- **THEN** the rule SHALL not report an error

#### Scenario: CSS-wide keywords accepted
- **WHEN** a property value is `inherit`, `initial`, `unset`, or `revert`
- **THEN** the rule SHALL not report an error

#### Scenario: `currentColor` accepted
- **WHEN** `@layer block` contains `.icon { color: currentColor; }`
- **THEN** the rule SHALL not report an error

#### Scenario: `transparent` accepted
- **WHEN** `@layer block` contains `.card { background: transparent; }`
- **THEN** the rule SHALL not report an error

#### Scenario: Grid fractions accepted
- **WHEN** `@layer block` contains `.layout { grid-template-columns: 1fr 2fr; }`
- **THEN** the rule SHALL not report an error

### Requirement: Token definition layers are excluded
The `reset`, `tokens`, and `global` layers SHALL be excluded from token enforcement because they are where tokens are defined.

#### Scenario: Raw value in global layer accepted
- **WHEN** `@layer global` contains `:root { --space-m: 1rem; }`
- **THEN** the rule SHALL not report an error

#### Scenario: Raw value in reset layer accepted
- **WHEN** `@layer reset` contains `* { box-sizing: border-box; margin: 0; }`
- **THEN** the rule SHALL not report an error

### Requirement: Duration and easing properties are token-enforced
Properties `transition-duration` and `animation-duration` SHALL require `var()` references.

#### Scenario: Duration token accepted
- **WHEN** `@layer block` contains `.card { transition-duration: var(--duration-fast); }`
- **THEN** the rule SHALL not report an error

#### Scenario: Raw duration rejected
- **WHEN** `@layer block` contains `.card { transition-duration: 150ms; }`
- **THEN** the rule SHALL report an error

### Requirement: Configurable property list
The list of properties that require `var()` SHALL be configurable via rule options.

#### Scenario: Custom properties list
- **WHEN** the rule is configured with `[true, { properties: ["padding", "color"] }]`
- **THEN** only `padding` and `color` SHALL be enforced
- **AND** other properties like `gap` or `font-size` SHALL be allowed with raw values
