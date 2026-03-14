## 1. Plugin Scaffold

- [x] 1.1 Create `frontend/stylelint-plugin-cube-css/` directory structure (`index.js`, `lib/utils/`, `lib/rules/`, `test/rules/`)
- [x] 1.2 Create `index.js` entry point that registers all 14 rules under the `cube/` namespace
- [x] 1.3 Create shared utility `lib/utils/get-layer-context.js` (walk PostCSS ancestors to find enclosing `@layer`)
- [x] 1.4 Create shared utility `lib/utils/is-var-function.js` (check if a value contains `var()`)
- [x] 1.5 Create shared utility `lib/utils/visual-properties.js` (set of visual treatment property names)

## 2. Tier 1 — Core Methodology Rules

- [x] 2.1 Implement `cube/require-layer` rule and tests
- [x] 2.2 Implement `cube/layer-order` rule and tests
- [x] 2.3 Implement `cube/exception-data-attr` rule and tests
- [x] 2.4 Implement `cube/no-visual-in-composition` rule and tests
- [x] 2.5 Implement `cube/utility-single-property` rule and tests
- [x] 2.6 Implement `cube/block-require-scope` rule and tests
- [x] 2.7 Implement `cube/require-token-variables` rule and tests (including calc() awareness, structural value allowlist, duration properties)

## 3. Tier 2 — Structural Rules

- [x] 3.1 Implement `cube/block-max-lines` rule and tests
- [x] 3.2 Implement `cube/one-block-per-file` rule and tests
- [x] 3.3 Implement `cube/prefer-where-in-reset` rule and tests
- [x] 3.4 Implement `cube/data-attr-naming` rule and tests

## 4. Tier 3 — Modern CSS Rules

- [x] 4.1 Implement `cube/prefer-vi-over-vw` rule and tests
- [x] 4.2 Implement `cube/require-container-name` rule and tests
- [x] 4.3 Implement `cube/prefer-color-mix` rule and tests

## 5. Integration

- [x] 5.1 Update `frontend/stylelint.config.js` to register plugin and configure all 14 rules
- [x] 5.2 Add `@scope` to `at-rule-no-unknown` ignore list in stylelint config
- [x] 5.3 Run `npm run lint:css` against existing CSS files and document violations
- [x] 5.4 Fix or suppress existing CSS violations to pass lint
- [x] 5.5 Run full `make check` to verify CI pipeline passes
