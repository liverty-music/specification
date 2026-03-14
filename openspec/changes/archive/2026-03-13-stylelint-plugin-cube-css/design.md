## Context

The frontend uses stylelint 16.x with ESM (`"type": "module"`). The existing config at `stylelint.config.js` already uses external plugins (`stylelint-use-logical`) and shared configs (`stylelint-config-standard`, `stylelint-config-clean-order`). The CUBE CSS methodology is documented in skill files (`~/.claude/skills/cube-css/`) but has no automated enforcement for structural rules like layer ordering, scope isolation, or design token usage.

All 14 rules need awareness of which `@layer` a declaration lives in — this "layer context" is the defining technical challenge.

## Goals / Non-Goals

**Goals:**
- Enforce all CUBE CSS methodology rules as stylelint errors
- Layer-aware rule evaluation (rules behave differently based on which `@layer` code is in)
- Zero external runtime dependencies (pure stylelint plugin using PostCSS AST)
- All rules individually configurable and disableable
- Comprehensive test coverage for each rule

**Non-Goals:**
- HTML-side enforcement (e.g., `class="[ block ] [ composition ]"` bracket grouping) — requires an HTML linter, not stylelint
- Auto-fix capabilities for structural rules (require-layer, layer-order) — too risky to auto-rewrite
- Publishing to npm as a public package (may happen later, but not in scope)

## Decisions

### 1. Package location: `frontend/stylelint-plugin-cube-css/` as a local directory

The plugin lives as a local directory within the frontend repo, referenced via `plugins: ['./stylelint-plugin-cube-css/index.js']` in `stylelint.config.js`.

**Alternatives considered:**
- **npm workspace package** — Over-engineering for a single-consumer plugin. The frontend repo is not a monorepo with workspaces.
- **Separate repo** — Adds cross-repo coordination overhead for something used only here. Can extract later if OSS demand arises.
- **Inline in `src/`** — `src/` is application code; linting tools belong at the project root level.

### 2. Layer context resolution: Walk the PostCSS AST ancestor chain

Each rule that needs layer awareness traverses the parent nodes of a declaration/rule to find the enclosing `@layer` AtRule. This is extracted into a shared utility `getLayerContext(node)` that returns the layer name (or `null` for unlayered code).

```
AtRule(@layer block)
  └─ AtRule(@scope .card)
       └─ Rule(:scope)
            └─ Declaration(padding: var(--space-m))
                 ↑ getLayerContext() → "block"
```

**Alternatives considered:**
- **Pre-pass to build a layer map** — More complex, harder to maintain, marginal performance benefit given typical file sizes.
- **File-path based detection** (e.g., `compositions/` → composition layer) — Brittle, doesn't work with bundled CSS or non-standard structures.

### 3. Plugin architecture: Single entry point, one file per rule

```
stylelint-plugin-cube-css/
  index.js                    # Plugin registration (exports all rules)
  lib/
    utils/
      get-layer-context.js    # Shared: walk ancestors to find @layer
      is-var-function.js      # Shared: check if a value contains var()
      visual-properties.js    # Shared: set of visual treatment properties
    rules/
      require-layer.js
      layer-order.js
      exception-data-attr.js
      no-visual-in-composition.js
      utility-single-property.js
      block-require-scope.js
      require-token-variables.js
      block-max-lines.js
      one-block-per-file.js
      prefer-where-in-reset.js
      data-attr-naming.js
      prefer-vi-over-vw.js
      require-container-name.js
      prefer-color-mix.js
  test/
    rules/
      require-layer.test.js
      ...                     # One test file per rule
```

Each rule file exports a standard stylelint rule object using `stylelint.createPlugin()`. Rules follow the naming convention `cube/<rule-name>`.

### 4. `require-token-variables` — calc() must contain at least one `var()`

When a property value uses `calc()`, the rule checks that at least one `var()` reference exists within the calc expression. Pure literal `calc()` expressions (e.g., `calc(16px + 4px)`) are rejected because they bypass the token system.

**Allowed structural values** that bypass the rule entirely: `0`, `auto`, `none`, `inherit`, `initial`, `unset`, `revert`, `currentColor`, `transparent`, fractions (`1fr`, `2fr`), and percentages used structurally (`100%`, `50%`).

**Ignored layers**: `reset` and `global` (where tokens are defined).

### 5. `block-require-scope` — `@scope` required in block layer

Within `@layer block`, all style rules must be wrapped in `@scope(<selector>)`. Direct rules without `@scope` are flagged. This enforces component isolation at the CSS level and eliminates the need for BEM prefixes.

### 6. Visual property set for `no-visual-in-composition`

The following properties are classified as "visual treatment" and disallowed in the composition layer:

- Color: `color`, `background`, `background-color`, `background-image`, `border-color`, `outline-color`
- Typography: `font-style`, `font-weight`, `text-decoration`, `text-transform`, `letter-spacing`
- Decorative: `box-shadow`, `text-shadow`, `border-radius`, `opacity`, `filter`, `backdrop-filter`
- Transitions: `transition`, `animation`

Allowed in composition: `display`, `flex-*`, `grid-*`, `gap`, `align-*`, `justify-*`, `margin-*`, `padding-*`, `inline-size`, `block-size`, `min-*`, `max-*`, `overflow`, `position`.

This set is configurable via rule options.

### 7. Testing: Vitest with stylelint's `lint()` API

Tests use `vitest` (already in the project) and invoke `stylelint.lint({ code, config })` directly to test each rule in isolation. No CSS files on disk needed — all test cases are inline strings.

## Risks / Trade-offs

**[R1] `@scope` browser support is "Baseline Newly Available"** → The project targets modern browsers only. The Aurelia 2 + Vite stack already assumes modern browser support. `@scope` is available in Chrome 118+, Edge 118+, Safari 17.4+, Firefox 128+.

**[R2] Existing CSS files will need migration** → Adding all 14 rules at once will produce many lint errors on existing files. Mitigation: configure new rules as `"warning"` initially, then promote to `"error"` after migration is complete.

**[R3] Layer context detection assumes `@layer` is always an ancestor AtRule** → CSS files that use `@import "file.css" layer(block)` won't have an `@layer` AtRule in the parsed AST of the imported file. Mitigation: document that each CSS file must include its own `@layer` wrapper (which aligns with the methodology's file organization pattern).

**[R4] Performance with 14 rules traversing the AST** → Each rule walks the tree independently. For typical component CSS files (< 200 lines), this is negligible. If performance becomes an issue, rules can be consolidated into a single AST walk later.
