## ADDED Requirements

### Requirement: `cube/exception-data-attr` requires `data-*` selectors in exception layer
Selectors inside `@layer exception` SHALL contain at least one `[data-*]` attribute selector. CSS-class-only exceptions are prohibited.

#### Scenario: Attribute selector accepted
- **WHEN** `@layer exception` contains `.card[data-state="reversed"] { ... }`
- **THEN** the rule SHALL not report an error

#### Scenario: Pure class selector rejected
- **WHEN** `@layer exception` contains `.card--reversed { ... }` (no `data-*` attribute)
- **THEN** the rule SHALL report an error: "Exception layer selectors must use [data-*] attribute selectors"

#### Scenario: Multiple data attributes accepted
- **WHEN** `@layer exception` contains `.card[data-state="loading"][data-variant="compact"] { ... }`
- **THEN** the rule SHALL not report an error

#### Scenario: Non-exception layers ignored
- **WHEN** `@layer block` contains `.card { ... }` (no `data-*` attribute)
- **THEN** the rule SHALL not report an error (rule only applies to exception layer)

### Requirement: `cube/no-visual-in-composition` prohibits visual properties in composition layer
The composition layer SHALL only contain structural/layout properties. Visual treatment properties SHALL be rejected.

#### Scenario: Layout properties accepted
- **WHEN** `@layer composition` contains `.cluster { display: flex; flex-wrap: wrap; gap: var(--cluster-gap, var(--space-s)); }`
- **THEN** the rule SHALL not report an error

#### Scenario: Color property rejected
- **WHEN** `@layer composition` contains `.flow { color: var(--color-text); }`
- **THEN** the rule SHALL report an error: "Visual property 'color' is not allowed in the composition layer"

#### Scenario: Background rejected
- **WHEN** `@layer composition` contains `.wrapper { background: var(--color-surface); }`
- **THEN** the rule SHALL report an error

#### Scenario: Box-shadow rejected
- **WHEN** `@layer composition` contains `.sidebar { box-shadow: 0 2px 4px oklch(0% 0 0 / 10%); }`
- **THEN** the rule SHALL report an error

#### Scenario: Border-radius rejected
- **WHEN** `@layer composition` contains `.grid { border-radius: var(--radius-m); }`
- **THEN** the rule SHALL report an error

#### Scenario: Custom visual property set via options
- **WHEN** the rule is configured with `additionalVisualProperties: ["cursor"]`
- **THEN** `cursor` SHALL also be rejected in the composition layer

### Requirement: `cube/utility-single-property` limits properties per utility selector
Each selector in `@layer utility` SHALL contain at most the configured number of properties (default: 2).

#### Scenario: Single property accepted
- **WHEN** `@layer utility` contains `.mt-s { margin-block-start: var(--space-s); }`
- **THEN** the rule SHALL not report an error

#### Scenario: Two tightly related properties accepted
- **WHEN** `@layer utility` contains `.visually-hidden { clip: rect(0 0 0 0); clip-path: inset(50%); }`
- **THEN** the rule SHALL not report an error (within default limit of 2)

#### Scenario: Too many properties rejected
- **WHEN** `@layer utility` contains `.badge { color: var(--color-primary); font-size: var(--step-0); padding: var(--space-xs); }`
- **THEN** the rule SHALL report an error: "Utility selectors must have at most 2 properties, found 3"

#### Scenario: Custom max configured
- **WHEN** the rule is configured with `[true, { max: 3 }]`
- **THEN** selectors with 3 or fewer properties SHALL be accepted

#### Scenario: visually-hidden pattern accepted with higher limit
- **WHEN** the rule is configured with `[true, { max: 6 }]`
- **AND** `@layer utility` contains `.visually-hidden` with 6 properties
- **THEN** the rule SHALL not report an error

### Requirement: `cube/block-require-scope` requires `@scope` in block layer
All style rules inside `@layer block` SHALL be wrapped in `@scope(<selector>)`.

#### Scenario: Scoped block accepted
- **WHEN** `@layer block` contains `@scope (.card) { :scope { padding: var(--space-m); } }`
- **THEN** the rule SHALL not report an error

#### Scenario: Unscoped block rejected
- **WHEN** `@layer block` contains `.card { padding: var(--space-m); }` (not inside `@scope`)
- **THEN** the rule SHALL report an error: "Block layer rules must be wrapped in @scope()"

#### Scenario: Nested rules inside scope accepted
- **WHEN** `@layer block` contains `@scope (.card) { :scope { ... } .title { ... } .content { ... } }`
- **THEN** the rule SHALL not report an error

#### Scenario: Non-block layers ignored
- **WHEN** `@layer composition` contains `.flow > * + * { ... }` (not inside `@scope`)
- **THEN** the rule SHALL not report an error (rule only applies to block layer)

### Requirement: `cube/data-attr-naming` restricts data attribute names in exception layer
Exception layer selectors SHALL only use `data-state`, `data-variant`, or `data-theme` attribute names.

#### Scenario: `data-state` accepted
- **WHEN** `@layer exception` contains `.card[data-state="loading"] { ... }`
- **THEN** the rule SHALL not report an error

#### Scenario: `data-variant` accepted
- **WHEN** `@layer exception` contains `.card[data-variant="compact"] { ... }`
- **THEN** the rule SHALL not report an error

#### Scenario: `data-theme` accepted
- **WHEN** `@layer exception` contains `[data-theme="dark"] { ... }`
- **THEN** the rule SHALL not report an error

#### Scenario: Non-standard data attribute rejected
- **WHEN** `@layer exception` contains `.card[data-reversed] { ... }`
- **THEN** the rule SHALL report an error: "Exception data attributes must use 'data-state', 'data-variant', or 'data-theme'. Found 'data-reversed'"

#### Scenario: Custom allowed attributes via options
- **WHEN** the rule is configured with `[true, { additionalAttributes: ["data-density"] }]`
- **THEN** `data-density` SHALL also be accepted
