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

Configured properties in the consumption layers (composition, utility, block, exception) must resolve to a `var()` reference rather than a raw literal — `padding: 16px` is rejected, `padding: var(--space-m)` is accepted. `transition-duration` and `animation-duration` are part of the default enforced property list alongside spacing, color, and typography properties, and the full list is configurable via a `properties` rule option so consumers can narrow enforcement (e.g. to only `padding` and `color`) without disabling the rule outright.

When a property value uses `calc()`, the rule checks that at least one `var()` reference exists within the calc expression. Pure literal `calc()` expressions (e.g., `calc(16px + 4px)`) are rejected because they bypass the token system.

**Allowed structural values** that bypass the rule entirely: `0`, `auto`, `none`, `inherit`, `initial`, `unset`, `revert`, `currentColor`, `transparent`, fractions (`1fr`, `2fr`), and percentages used structurally (`100%`, `50%`).

**Ignored layers**: `reset` and `global` (where tokens are defined).

### 8. Tier 1 layer rules: `require-layer`, `layer-order`, `exception-data-attr`, `data-attr-naming`, `utility-single-property`

`require-layer` flags any CSS rule that sits outside an `@layer` block; `@layer` order-declaration statements (e.g. `@layer reset, global, composition, utility, block, exception;`) and at-rules that cannot live inside `@layer` (`@property`) are exempt, but `@keyframes` outside `@layer` is still flagged. `layer-order` requires the layer sequence — whether written as a declaration statement or as the order block-form `@layer` rules appear in the file — to follow `reset, global, composition, utility, block, exception`; subsets are allowed as long as their relative order is preserved, and an unrecognized layer name is rejected. `exception-data-attr` requires every selector inside `@layer exception` to carry at least one `[data-*]` attribute selector, rejecting exceptions expressed as plain modifier classes; `data-attr-naming` narrows those attributes to `data-state`, `data-variant`, or `data-theme` by default, extensible via an `additionalAttributes` option. `utility-single-property` caps each `@layer utility` selector at 2 properties by default (configurable via `max`), so utilities stay single-purpose.

### 9. Tier 2/3 rules: `block-max-lines`, `one-block-per-file`, `prefer-where-in-reset`, `prefer-vi-over-vw`, `require-container-name`, `prefer-color-mix`

`block-max-lines` caps each `@scope` block inside `@layer block` at 80 lines by default (configurable via `max`), pushing oversized components to be decomposed rather than grown. `one-block-per-file` limits a file containing `@layer block` to a single `@scope` directive, keeping block CSS one-component-per-file. `prefer-where-in-reset` warns (does not error) when `@layer reset`/`@layer global` selectors skip `:where()` wrapping, with `:root` and `body` exempted as standard global singletons. `prefer-vi-over-vw` rejects `vw`/`svw`/`lvw` in favor of the writing-mode-aware `vi`/`svi`/`lvi` units, leaving `vh` untouched. `require-container-name` requires any rule declaring a non-`normal` `container-type` (or the `container` shorthand) to also name the container. `prefer-color-mix` warns when a custom property in `@layer global` appears to derive a color from another token without using `color-mix()` or relative color syntax.

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
