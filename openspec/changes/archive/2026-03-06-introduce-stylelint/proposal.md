## Why

The frontend uses Biome for JavaScript/TypeScript linting and formatting, but has no automated enforcement of CSS coding standards. The `modern-css-platform` spec defines requirements for Container Queries, Logical Properties, OKLCH color, and View Transitions, yet nothing prevents developers from writing legacy `rgb()`, physical `margin-left`, or viewport-based `@media (width)` queries. Stylelint closes this gap by turning spec requirements into enforceable lint rules.

## What Changes

- Configure Stylelint with `stylelint-config-standard` + `stylelint-config-clean-order` to enforce modern CSS standards
- Add rules that **disallow legacy patterns**:
  - Legacy color functions (`rgb`, `rgba`, `hsl`, `hsla`, hex) in favor of `oklch()`
  - Physical directional properties (`margin-left`, `top`, `float`, etc.) in favor of CSS Logical Properties (`margin-inline-start`, `inset-block-start`, etc.)
  - Viewport-width media features (`width`, `min-width`, `max-width`) in `@media` in favor of `@container` queries
  - `z-index`, `!important`, `float`, `clear` as anti-patterns
- Add rules that **enforce quality**:
  - Selector specificity ceiling (`0,4,0`), no ID selectors
  - Property declaration ordering (Interaction > Position > Layout > Box > Typography > Visual > Animation)
  - Precision limits, deprecated property/media-type detection
- Migrate all existing CSS files (~66 `rgb`/`rgba` occurrences, ~14 physical property usages, 1 viewport media query) to comply with the new rules
- Integrate Stylelint into `make lint` and `make check` (CI gate)

## Capabilities

### New Capabilities
- `css-linting`: Defines Stylelint configuration, rule rationale, Tailwind v4 compatibility settings, and CI integration requirements

### Modified Capabilities
- `modern-css-platform`: Adds the enforcement mechanism (Stylelint rules) for existing requirements around Container Queries, Logical Properties, and OKLCH color. No new requirements, but the spec gains a "Tooling Enforcement" section linking rules to requirements.

## Impact

- **frontend repo**: All 11 CSS files under `src/` will be modified (color migration, logical properties, property reorder)
- **Dependencies**: Add `stylelint-order` and `stylelint-config-clean-order` npm packages
- **CI**: `make lint` / `make check` already calls `npm run lint:css`; no CI config change needed
- **DX**: Developers writing new CSS will get immediate lint errors for legacy patterns
