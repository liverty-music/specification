## ADDED Requirements

### Requirement: `cube/block-max-lines` limits block size
Each `@scope` block inside `@layer block` SHALL contain at most the configured number of lines (default: 80).

#### Scenario: Small block accepted
- **WHEN** `@layer block` contains a `@scope (.card) { ... }` block with 40 lines
- **THEN** the rule SHALL not report an error

#### Scenario: Oversized block rejected
- **WHEN** `@layer block` contains a `@scope (.card) { ... }` block with 95 lines
- **THEN** the rule SHALL report an error: "Block exceeds 80 lines (found 95). Push work to higher layers."

#### Scenario: Custom max configured
- **WHEN** the rule is configured with `[true, { max: 120 }]`
- **THEN** blocks up to 120 lines SHALL be accepted

#### Scenario: Non-block layers ignored
- **WHEN** `@layer global` contains a rule set spanning 200 lines
- **THEN** the rule SHALL not report an error

### Requirement: `cube/one-block-per-file` enforces single block per file
Files containing `@layer block` SHALL have at most one `@scope` directive.

#### Scenario: Single scope accepted
- **WHEN** a CSS file contains `@layer block { @scope (.card) { ... } }`
- **THEN** the rule SHALL not report an error

#### Scenario: Multiple scopes rejected
- **WHEN** a CSS file contains `@layer block { @scope (.card) { ... } @scope (.button) { ... } }`
- **THEN** the rule SHALL report an error: "Block layer must contain only one @scope. Found 2. Use separate files."

#### Scenario: Files without block layer ignored
- **WHEN** a CSS file contains only `@layer composition { ... }`
- **THEN** the rule SHALL not report an error

### Requirement: `cube/prefer-where-in-reset` recommends `:where()` in reset and global layers
Selectors in `@layer reset` and `@layer global` SHOULD use `:where()` wrapping for zero-specificity defaults.

#### Scenario: `:where()` selector accepted
- **WHEN** `@layer global` contains `:where(h1, h2, h3) { line-height: 1.2; }`
- **THEN** the rule SHALL not report an error

#### Scenario: Element selector without `:where()` warned
- **WHEN** `@layer global` contains `h1, h2, h3 { line-height: 1.2; }`
- **THEN** the rule SHALL report a warning: "Consider wrapping in :where() for zero-specificity defaults"

#### Scenario: `:root` selector accepted without `:where()`
- **WHEN** `@layer global` contains `:root { --color-primary: oklch(55% 0.25 260); }`
- **THEN** the rule SHALL not report an error (`:root` for custom properties is a standard pattern)

#### Scenario: `body` selector accepted without `:where()`
- **WHEN** `@layer global` contains `body { font-family: var(--font-base); }`
- **THEN** the rule SHALL not report an error (`body` is a common global singleton)

#### Scenario: Universal selector in reset accepted
- **WHEN** `@layer reset` contains `:where(*, *::before, *::after) { box-sizing: border-box; }`
- **THEN** the rule SHALL not report an error

#### Scenario: Non-reset/global layers ignored
- **WHEN** `@layer block` contains `.card { ... }` without `:where()`
- **THEN** the rule SHALL not report an error
