## Context

The frontend uses Biome for JS/TS linting and formatting but lacks automated CSS quality enforcement. The `modern-css-platform` spec mandates Container Queries, Logical Properties, OKLCH color, and View Transitions, yet no tooling prevents developers from using legacy patterns. The codebase already has Stylelint v16 + `stylelint-config-standard` installed with a minimal configuration. This change expands that configuration into a comprehensive modern CSS enforcement layer.

Current state:
- 11 CSS files under `frontend/src/`
- ~66 `rgb()`/`rgba()` usages (partial OKLCH migration already started)
- ~14 physical directional property usages (`margin-left`, `top`, `left`, etc.)
- 1 viewport-width `@media` query that should be `@container`
- 0 `z-index`, 0 `float`, 0 `!important` usages (already clean)
- Biome handles CSS parsing/formatting (`tailwindDirectives: true`); Stylelint handles CSS linting

## Goals / Non-Goals

**Goals:**
- Enforce modern CSS standards (OKLCH, Logical Properties, Container Queries) via lint rules
- Prevent anti-patterns (z-index, !important, float, high specificity) from entering the codebase
- Standardize property declaration ordering for readability
- Migrate all existing CSS to comply with the new rules in a single pass
- Zero CI configuration changes (existing `make lint` pipeline already invokes `npm run lint:css`)

**Non-Goals:**
- Replacing Biome's CSS formatting — Biome handles formatting, Stylelint handles linting
- SCSS/Sass support — the project uses plain CSS + Tailwind v4
- Custom Stylelint plugin development — use only built-in rules and maintained community plugins
- Enforcing `@container` over `@media` for non-width features (e.g., `prefers-reduced-motion`, `prefers-color-scheme` remain as `@media`)

## Decisions

### Decision 1: Stylelint over alternatives

**Choice**: Stylelint with `stylelint-config-standard`

**Alternatives considered**:
| Option | Pros | Cons |
|--------|------|------|
| Biome CSS linting | Already installed, single tool | Only a handful of CSS lint rules; no property order, no specificity, no function disallow |
| @eslint/css | Baseline browser compat checking (`use-baseline`) | ~6 rules total; ESLint not used in this project; would add a third linter |
| Stylelint | 170+ rules, mature ecosystem, property order plugin, active maintenance | Additional tool alongside Biome |

**Rationale**: Stylelint is the only tool with sufficient rule coverage to enforce modern CSS standards. Biome's CSS linting is too immature. Adding ESLint solely for CSS is unjustified when the project already uses Biome for JS/TS.

### Decision 2: Error severity for all rules (no warning phase)

**Choice**: All custom rules emit errors, not warnings. Existing code is migrated in the same PR.

**Rationale**: The codebase is small (11 files). A phased warning-to-error approach adds unnecessary process overhead. Migrating rgb/rgba to oklch in one pass is feasible and delivers immediate value.

### Decision 3: Full physical property ban including positional properties

**Choice**: Ban `top`, `right`, `bottom`, `left` in addition to `margin-*`, `padding-*`, `border-*` physical variants.

**Alternatives considered**:
- Ban only margin/padding/border physicals, allow positional (`top`/`left`)
- Ban nothing, rely on code review

**Rationale**: `inset-block-start`, `inset-inline-start`, and `inset` shorthand are Baseline Widely Available (Chrome 87+, Firefox 63+, Safari 14.1+). The codebase already uses `inset: 0` extensively. The 5 remaining `top`/`left`/`bottom` usages have direct logical equivalents. Full ban prevents future regression.

### Decision 4: Property ordering via `stylelint-config-clean-order`

**Choice**: Use `stylelint-config-clean-order` (wraps `stylelint-order` plugin).

**Rationale**: Provides an opinionated, logical grouping (Interaction > Position > Layout > Box Model > Typography > Appearance > Transition) with autofix support. Avoids maintaining a custom order list. One-time `stylelint --fix` reformats all files.

### Decision 5: Viewport-width media features disallowed

**Choice**: Disallow `width`, `min-width`, `max-width` in `@media` via `media-feature-name-disallowed-list`.

**Rationale**: Aligns with `modern-css-platform` spec requirement for Container Queries. `@media` with `prefers-reduced-motion`, `prefers-color-scheme`, and other non-width features remain allowed. Only 1 existing usage needs migration.

### Decision 6: Tailwind v4 at-rule compatibility

**Choice**: Whitelist `@theme`, `@layer`, `@container`, `@starting-style`, `@property` in `at-rule-no-unknown`.

**Rationale**: Tailwind v4 uses CSS-native `@theme` directive. Modern CSS features (`@starting-style`, `@property`, `@container`) are already in use in the codebase and must not be flagged as unknown.

## Risks / Trade-offs

**[Risk] OKLCH color conversion accuracy** — Converting 66+ `rgb()`/`rgba()` values to `oklch()` may introduce subtle color shifts.
  - Mitigation: Use a conversion tool and visually verify key screens (discover page starfield, loading sequence gradients). OKLCH is perceptually uniform, so differences should be minimal.

**[Risk] Property order autofix changes large diffs** — Running `stylelint --fix` for property ordering will reformat all 11 CSS files.
  - Mitigation: Apply ordering fix in a dedicated commit before other changes, making code review clearer.

**[Risk] `text-align: center` flagged as physical property** — `center` is not directional (unlike `left`/`right`).
  - Mitigation: Only `text-align: left` and `text-align: right` need migration to `start`/`end`. `text-align: center` is not affected by `property-disallowed-list` since we ban physical properties, not values.

**[Risk] `env(safe-area-inset-bottom)` uses physical naming** — The environment variable name is a browser API, not changeable.
  - Mitigation: The containing property changes to logical (`padding-block-end`) while the env() value remains as-is. This is acceptable.

**[Trade-off] Longer property names** — `margin-block-start` is more verbose than `margin-top`.
  - Accepted: Shorthand forms (`margin-block`, `padding-inline`, `inset`) reduce verbosity. RTL/i18n correctness outweighs brevity.
