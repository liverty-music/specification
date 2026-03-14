## ADDED Requirements

### Requirement: `cube/require-layer` rejects CSS rules outside `@layer` blocks
All CSS rules SHALL be inside an `@layer` block. Unlayered styles override all layers and break the CUBE CSS cascade.

#### Scenario: Rule inside `@layer` accepted
- **WHEN** a CSS file contains `.card { padding: var(--space-m); }` inside `@layer block { ... }`
- **THEN** the rule SHALL not report an error

#### Scenario: Rule outside `@layer` rejected
- **WHEN** a CSS file contains `.card { padding: var(--space-m); }` at the top level (not inside any `@layer`)
- **THEN** the rule SHALL report an error: "All CSS rules must be inside an @layer block"

#### Scenario: `@layer` declaration statement accepted
- **WHEN** a CSS file contains `@layer reset, global, composition, utility, block, exception;` (a layer order declaration with no body)
- **THEN** the rule SHALL not report an error (declarations are not rules)

#### Scenario: `@property` at top level accepted
- **WHEN** a CSS file contains `@property --hue { syntax: "<number>"; inherits: true; initial-value: 260; }` outside `@layer`
- **THEN** the rule SHALL not report an error (`@property` cannot be inside `@layer`)

#### Scenario: `@keyframes` outside `@layer` rejected
- **WHEN** a CSS file contains `@keyframes fade-in { ... }` at the top level
- **THEN** the rule SHALL report an error

### Requirement: `cube/layer-order` enforces correct `@layer` declaration order
The `@layer` declaration statement SHALL list layers in the order: `reset, global, composition, utility, block, exception`. Subsets are allowed but order must be preserved.

#### Scenario: Correct full order accepted
- **WHEN** a CSS file contains `@layer reset, global, composition, utility, block, exception;`
- **THEN** the rule SHALL not report an error

#### Scenario: Correct partial order accepted
- **WHEN** a CSS file contains `@layer composition, utility, block;` (subset in correct relative order)
- **THEN** the rule SHALL not report an error

#### Scenario: Wrong order rejected
- **WHEN** a CSS file contains `@layer block, utility, composition;`
- **THEN** the rule SHALL report an error: "Layer order must follow: reset, global, composition, utility, block, exception"

#### Scenario: Unknown layer name rejected
- **WHEN** a CSS file contains `@layer reset, global, components;` (where `components` is not a valid CUBE CSS layer name)
- **THEN** the rule SHALL report an error: "Unknown layer name 'components'. Expected one of: reset, global, composition, utility, block, exception"

#### Scenario: Multiple `@layer` block declarations maintain order
- **WHEN** a CSS file contains `@layer composition { ... }` followed by `@layer block { ... }`
- **THEN** the rule SHALL not report an error (composition before block is correct order)

#### Scenario: Out-of-order `@layer` block declarations rejected
- **WHEN** a CSS file contains `@layer block { ... }` followed by `@layer composition { ... }`
- **THEN** the rule SHALL report an error
