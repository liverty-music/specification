## Why

The frontend CSS is currently a mix of Tailwind utility classes in HTML templates (22 of 26 files) and component-colocated CSS files with no `@layer` structure. This conflicts with CUBE CSS methodology — which emphasizes cascade-driven, semantic styling — and makes the codebase harder to reason about. PR #156 introduced a stylelint plugin enforcing CUBE CSS rules, producing 202 warnings across 14 CSS files. Now is the time to resolve those warnings and fully migrate to CUBE CSS while removing the Tailwind dependency entirely.

## What Changes

- **Remove TailwindCSS dependency** — delete `@import "tailwindcss"`, `@tailwindcss/vite` plugin, and npm packages. Replace Tailwind's preflight with a custom reset, `@theme` tokens with plain CSS custom properties, and utility classes with CUBE composition/utility/block CSS.
- **Establish CUBE CSS `@layer` architecture** — create `src/styles/main.css` as the CSS entry point with explicit `@layer` ordering: `reset, tokens, global, composition, utility, block, exception`.
- **Decompose `my-app.css`** — split the monolithic 243-line file into `tokens.css`, `reset.css`, `global.css`, `compositions.css`, `utilities.css` under `src/styles/`, plus a residual `my-app.css` as a block-layer component CSS.
- **Migrate component CSS to `@layer block { @scope }`** — wrap each component's colocated CSS in `@layer block { @scope(<component-selector>) { ... } }`.
- **Rewrite HTML templates** — remove all Tailwind utility classes from 22 HTML files; replace with CUBE composition classes, utility classes, or absorb into block-scoped CSS.

## Capabilities

### New Capabilities

- `cube-css-architecture`: Defines the CUBE CSS layer structure (`src/styles/`), file organization, `@layer` ordering, and the relationship between global styles and component-colocated block CSS.

### Modified Capabilities

- `design-system`: Design tokens move from Tailwind `@theme` to plain CSS custom properties in `tokens.css`. Token names and values are preserved; only the delivery mechanism changes.
- `modern-css-platform`: Adds `@layer`, `@scope`, and explicit cascade ordering as foundational CSS patterns. Removes Tailwind as a dependency.

## Impact

- **Frontend repo only** — no backend or specification changes.
- **All 14 CSS files** — restructured into CUBE layers.
- **22 HTML template files** — Tailwind classes removed and replaced.
- **Build config** — `vite.config.ts` loses `@tailwindcss/vite` plugin.
- **Dependencies** — `tailwindcss` and `@tailwindcss/vite` removed from `package.json`.
- **Stylelint** — existing 202 warnings should reduce to 0 after migration.
- **Visual regression risk** — high during migration; each component PR should be visually verified.
