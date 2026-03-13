## Context

The frontend currently uses TailwindCSS v4 for design tokens (`@theme`), CSS reset (Preflight), and utility class generation. 22 of 26 HTML templates embed Tailwind utility classes directly. Component CSS files (14 total, 202 stylelint warnings) have no `@layer` structure. PR #156 introduced a custom stylelint plugin enforcing CUBE CSS methodology rules — all as warnings to allow gradual migration.

The goal is to replace Tailwind entirely with CUBE CSS architecture: a cascade-driven, `@layer`-ordered system where Global styles do the heavy lifting, Composition primitives control layout, and Block-scoped CSS handles component-specific overrides.

## Goals / Non-Goals

**Goals:**

- Establish `@layer` ordering (reset, tokens, global, composition, utility, block, exception) as the cascade foundation
- Replace Tailwind `@theme` with plain CSS custom properties in `tokens.css`
- Replace Tailwind Preflight with a custom reset
- Decompose `my-app.css` (243 lines) into CUBE-layered files under `src/styles/`
- Migrate all 14 component CSS files to `@layer block { @scope() { ... } }`
- Remove all Tailwind utility classes from 22 HTML templates
- Achieve 0 stylelint warnings (currently 202)
- Remove `tailwindcss` and `@tailwindcss/vite` from dependencies

**Non-Goals:**

- Redesigning the visual appearance — token values and visual output remain identical
- Adding new features or pages during migration
- Introducing a CSS preprocessor (Sass, PostCSS plugins) — pure CSS only
- Creating a comprehensive utility class library — CUBE philosophy favors Global + Composition over utilities

## Decisions

### Decision 1: File structure — `src/styles/` with `main.css` as entry point

```
src/
  styles/
    main.css           ← CSS entry point: @layer declarations + @import ordering
    tokens.css         ← Design tokens as CSS custom properties
    reset.css          ← Browser reset (replaces Tailwind Preflight)
    global.css         ← CUBE Global: base element styles, fluid typography
    compositions.css   ← CUBE Composition: layout primitives (.cluster, .stack, etc.)
    utilities.css      ← CUBE Utility: single-purpose classes + animation keyframes

  my-app.css           ← @layer block { @scope(my-app) { app shell layout } }
  components/
    <name>/<name>.css  ← @layer block { @scope(<element>) { ... } }
  routes/
    <name>/<name>.css  ← @layer block { @scope(<element>) { ... } }
```

`main.ts` imports `./styles/main.css`. Component CSS files remain colocated with their Aurelia components.

**Why not a single file?** CUBE CSS layers have distinct responsibilities. Separate files make it clear which layer a style belongs to and prevent accidental cross-layer leakage.

**Why `main.css` not `my-app.css` as entry point?** `my-app.css` is Aurelia's convention for the `my-app` component's colocated CSS. Using it as the global entry point conflates "app shell component styles" with "entire application's CSS architecture." `main.css` pairs with `main.ts` (the bootstrap file) and clearly means "the CSS entry point."

### Decision 2: `@layer` ordering — CUBE layers declared in `main.css`

```css
/* src/styles/main.css */
@layer reset, tokens, global, composition, utility, block, exception;

@import './reset.css' layer(reset);
@import './tokens.css' layer(tokens);
@import './global.css' layer(global);
@import './compositions.css' layer(composition);
@import './utilities.css' layer(utility);
```

`tokens` is a dedicated layer between reset and global. Tokens define values (`:root` custom properties); global applies them to elements. Separating these concerns makes it clear that `tokens.css` should only contain custom property definitions, not style rules.

Block and exception layers are populated by component CSS files via `@layer block { ... }` declarations in each file.

**Why this order?** Follows CUBE CSS cascade philosophy: reset (lowest) → tokens (design values) → global (element defaults) → composition (layout) → utility (overrides) → block (component-specific) → exception (state deviations). Each layer can override the previous.

### Decision 3: Tailwind removal — phased approach with co-existence

Tailwind cannot be removed in one PR without breaking 22 HTML files. The migration uses a phased approach:

1. **PR 1 (Foundation)**: Create `src/styles/` infrastructure, import alongside existing Tailwind. Both systems co-exist.
2. **PR 2-N (Component migration)**: One component per PR — migrate its CSS to `@layer block { @scope }` and rewrite its HTML to remove Tailwind classes. Absorb Tailwind utilities into Global/Composition/Block CSS.
3. **PR Last (Cleanup)**: Remove `@import "tailwindcss"`, `@tailwindcss/vite` plugin, and npm packages.

**Why not all at once?** A single PR touching 36+ files (14 CSS + 22 HTML) is unreviewable and high-risk for visual regressions. Component-by-component migration keeps PRs small and allows visual verification per component.

### Decision 4: Spacing philosophy — parent controls gap, children use fluid padding

Replace Tailwind's per-element spacing utilities (`px-4 py-3 mb-2 gap-2`) with CUBE CSS spacing principles:

- **Parent controls inter-child spacing** via `gap` (grid/flex) or the `.flow` composition (lobotomized owl `> * + *`).
- **Children never set external margin** — margin is the parent's responsibility.
- **Internal padding uses `clamp()`** for fluid, container-responsive sizing.
- **Spacing scale** defined as CSS custom properties in `tokens.css`.

### Decision 5: Reset strategy — custom reset, not a library

Write a minimal reset in `reset.css` using `:where()` for zero specificity:

```css
@layer reset {
  :where(*, *::before, *::after) { box-sizing: border-box; margin: 0; padding: 0; }
  :where(html) { -webkit-text-size-adjust: none; text-size-adjust: none; }
  :where(img, picture, video, canvas, svg) { display: block; max-inline-size: 100%; }
  :where(input, button, textarea, select) { font: inherit; }
  :where(body) { min-block-size: 100dvh; }
}
```

**Why `:where()`?** Zero specificity means any subsequent layer (global, utility, block) can override without specificity battles. This is a CUBE CSS best practice.

**Why not `modern-normalize`?** It adds opinions we don't need and doesn't use `:where()` for zero specificity. A minimal custom reset aligned with our specific needs is more maintainable.

### Decision 6: Global layer — "do as much as you can here"

Following Andy Bell's principle, `global.css` handles:

- Base typography: `body` font, fluid type scale with `clamp()`, `h1`-`h6` defaults
- Base element styles: `a`, `button`, `input`, `svg` — styled without classes
- Dark theme defaults: `body` background, text color from tokens
- View transition styles: `::view-transition-old/new(root)`

The goal is that **bare HTML elements look correct without any classes**. Block CSS only handles deviations from these defaults.

### Decision 7: Composition primitives — start minimal, extract as needed

Initial compositions based on current Tailwind usage patterns:

| Composition | Replaces | Purpose |
|-------------|----------|---------|
| `.flow` | `space-y-*` / manual `mb-*` | Vertical rhythm via lobotomized owl (`> * + *`) |
| `.stack` | `flex flex-col gap-*` | Vertical stacking with flexbox gap |
| `.cluster` | `flex items-center gap-*` | Horizontal inline grouping with wrapping |
| `.center` | `flex items-center justify-center` | Centering content |
| `.wrapper` | `max-w-md w-full px-4` | Max-width content wrapper with inline padding |
| `.grid-auto` | `grid grid-cols-* gap-*` | Auto-fit responsive grid |

Additional compositions will be extracted during component migration as patterns emerge. Do not pre-create compositions that aren't needed yet.

### Decision 8: HTML class notation — CUBE grouping convention

```html
<div class="[ card ] [ stack ] [ text-muted ]">
```

- `[ block ]` — component-specific class (matched by `@scope`)
- `[ composition ]` — layout primitive
- `[ utility ]` — single-purpose override

Brackets are optional sugar for readability; CSS treats them as part of the class list (they're ignored). This convention makes it easy to see which layer each class belongs to.

## Risks / Trade-offs

**[Visual regression during migration]** → Each component PR must be visually verified in the dev server. Consider adding Playwright visual regression snapshots for critical components.

**[Tailwind + CUBE co-existence during migration]** → Both systems' `@layer` declarations will be active simultaneously. Tailwind's layers (`base`, `components`, `utilities`) and CUBE's layers will co-exist. This is safe because they use different layer names and the explicit `@layer` declaration in `main.css` establishes the CUBE order. Tailwind's generated classes remain functional until removed from HTML.

**[Larger initial effort for Global layer]** → Writing `global.css` properly (fluid typography, base element styles) takes more upfront work than Tailwind's Preflight. But this is a one-time investment that reduces per-component work significantly — if Global is good, Block CSS is minimal.

**[Loss of Tailwind's utility generation]** → No auto-generated utility classes. Hand-written compositions and utilities must be maintained. Trade-off: fewer utilities, but each one is intentional and documented. CUBE philosophy favors fewer classes overall.

**[Stale Tailwind classes during migration]** → Between PR 1 and PR Last, some HTML files will still use Tailwind classes. Stylelint warnings will decrease incrementally, not all at once. Track progress via `npm run lint:css` warning count.
