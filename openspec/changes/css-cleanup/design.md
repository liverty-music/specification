## Context

The `improve-css-design` change migrated from TailwindCSS to CUBE CSS architecture. During that migration, several pragmatic shortcuts were taken:
- One `stylelint-disable-next-line` comment bypasses the `z-index` ban in `live-highway.css`
- The `css-linting` spec still contains a "Stylelint compatible with Tailwind CSS v4" requirement that is now dead
- The `stylelint.config.js` still allows `@theme` in `ignoreAtRules` (Tailwind remnant)

## Goals / Non-Goals

**Goals:**
- Eliminate all `stylelint-disable` comments by fixing the underlying issues
- Replace `z-index` with proper stacking context management (`isolation: isolate`)
- Remove obsolete Tailwind references from specs and lint config
- Consolidate duplicate `@keyframes` into `utilities.css`
- Add `prefers-contrast` / `forced-colors` accessibility support

**Non-Goals:**
- Refactoring TS/CSS state separation (that's `css-state-separation`)
- Adding Container Queries, View Transitions, or other modern CSS features (that's `css-modern-patterns`)
- Redesigning visual appearance of components

## Decisions

### Decision 1: Replace z-index with `isolation: isolate`

The `z-index: 10` in `.stage-header` (sticky header) is used to stack above scrolling content. Since `position: sticky` already creates a stacking context, and the header only needs to stack above its siblings within the same parent, `isolation: isolate` on the parent container achieves the same result without an arbitrary z-index value.

**Alternative**: Create a z-index token scale (e.g., `--z-sticky: 10`). Rejected because CUBE CSS philosophy prefers eliminating z-index entirely via proper stacking contexts.

### Decision 2: Remove Tailwind at-rule allowances

Remove `@theme` from `ignoreAtRules` in `stylelint.config.js` and `theme()` from `ignoreFunctions`. These were needed for Tailwind v4 compatibility but serve no purpose now.

### Decision 3: Keyframes consolidation into utilities.css

Any `@keyframes` definition that appears in both a component CSS file and `utilities.css` should exist only in `utilities.css` within `@layer utility`. Component CSS files should reference the animation by name without redefining the keyframes.

## Risks / Trade-offs

- [Risk] Removing `z-index` from `live-highway.css` could break the sticky header stacking in edge cases → Test with the live-highway component to verify the sticky header renders above scrolling content
- [Risk] Removing `@theme` from `ignoreAtRules` could break if any CSS file still references it → Grep codebase for `@theme` usage before removing
