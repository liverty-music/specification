## Why

The CUBE CSS methodology defines strict rules for how CSS should be organized across layers (Composition, Utility, Block, Exception), but these rules are currently enforced only by developer discipline and AI skill files. The existing `css-linting` spec covers modern CSS features (OKLCH, logical properties, container queries) but has no enforcement for CUBE CSS structural rules — such as requiring `@layer`, enforcing layer order, restricting what properties appear in which layer, or requiring `@scope` in blocks. A custom stylelint plugin closes this gap by making CUBE CSS methodology violations a lint error.

## What Changes

- Create a new `stylelint-plugin-cube-css` package in the frontend workspace containing 14 custom stylelint rules
- Integrate the plugin into the existing `stylelint.config.js` configuration
- Rules enforce all three tiers of CUBE CSS methodology:
  - **Tier 1 — Core methodology**: `@layer` usage, layer ordering, exception patterns, composition purity, utility scope, block scoping with `@scope`, and design token enforcement via `var()`
  - **Tier 2 — Structural enforcement**: block size limits, one-block-per-file, `:where()` in reset/global, and `data-*` attribute naming conventions
  - **Tier 3 — Modern CSS best practices**: `vi` over `vw`, `container-name` requirement, `color-mix()` preference

## Capabilities

### New Capabilities
- `cube-css-lint-plugin`: The stylelint plugin package itself — rule implementations, test suite, and plugin registration
- `cube-css-layer-enforcement`: Rules that enforce `@layer` structure (`require-layer`, `layer-order`)
- `cube-css-layer-constraints`: Rules that constrain what is allowed within each layer (`no-visual-in-composition`, `utility-single-property`, `block-require-scope`, `exception-data-attr`, `data-attr-naming`)
- `cube-css-token-enforcement`: The `require-token-variables` rule — enforces `var()` for design tokens in consumption layers, with `calc()` awareness
- `cube-css-structural-rules`: Rules enforcing file/block structure (`block-max-lines`, `one-block-per-file`, `prefer-where-in-reset`)
- `cube-css-modern-css-rules`: Rules enforcing modern CSS best practices (`prefer-vi-over-vw`, `require-container-name`, `prefer-color-mix`)

### Modified Capabilities
- `css-linting`: The existing stylelint configuration will be updated to register and configure the new plugin rules

## Impact

- **frontend/**: New package added (likely `packages/stylelint-plugin-cube-css/` or inline within `src/`)
- **frontend/stylelint.config.js**: Updated to include the plugin and configure all 14 rules
- **CI pipeline**: No changes needed — `make lint` already runs stylelint
- **Existing CSS files**: May need updates to comply with new rules (e.g., adding `@layer` wrappers, `@scope` in blocks, replacing magic values with `var()`)
- **Dependencies**: `stylelint` peer dependency (already installed)
