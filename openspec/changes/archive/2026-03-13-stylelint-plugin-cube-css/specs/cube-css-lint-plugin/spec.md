## ADDED Requirements

### Requirement: Plugin registers all rules under the `cube/` namespace
The plugin SHALL export all rules prefixed with `cube/` so they can be configured individually in `stylelint.config.js`.

#### Scenario: All 14 rules are registered
- **WHEN** the plugin is loaded by stylelint
- **THEN** the following rules SHALL be available: `cube/require-layer`, `cube/layer-order`, `cube/exception-data-attr`, `cube/no-visual-in-composition`, `cube/utility-single-property`, `cube/block-require-scope`, `cube/require-token-variables`, `cube/block-max-lines`, `cube/one-block-per-file`, `cube/prefer-where-in-reset`, `cube/data-attr-naming`, `cube/prefer-vi-over-vw`, `cube/require-container-name`, `cube/prefer-color-mix`

#### Scenario: Unknown rule name rejected
- **WHEN** a user configures `cube/nonexistent-rule` in their stylelint config
- **THEN** stylelint SHALL report an invalid configuration error

### Requirement: Plugin is a local ESM package
The plugin SHALL be implemented as a local ESM directory at `frontend/stylelint-plugin-cube-css/` and referenced via a relative path in the stylelint config.

#### Scenario: Plugin loaded via relative path
- **WHEN** `stylelint.config.js` includes `plugins: ['./stylelint-plugin-cube-css/index.js']`
- **THEN** stylelint SHALL load and register all plugin rules without errors

### Requirement: Each rule has comprehensive test coverage
Every rule SHALL have a dedicated test file with passing and failing test cases using vitest and stylelint's `lint()` API.

#### Scenario: Test suite passes
- **WHEN** `npx vitest run stylelint-plugin-cube-css/` is executed
- **THEN** all tests SHALL pass with zero failures

### Requirement: Shared layer context utility
The plugin SHALL provide a shared `getLayerContext(node)` utility that returns the name of the enclosing `@layer` for any PostCSS node.

#### Scenario: Nested node returns correct layer
- **WHEN** a declaration is nested inside `@layer block { @scope (.card) { :scope { ... } } }`
- **THEN** `getLayerContext()` SHALL return `"block"`

#### Scenario: Unlayered node returns null
- **WHEN** a declaration is not inside any `@layer` block
- **THEN** `getLayerContext()` SHALL return `null`
