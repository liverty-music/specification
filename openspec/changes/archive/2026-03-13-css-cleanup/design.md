## Context

The `improve-css-design` change migrated from TailwindCSS to CUBE CSS architecture. During that migration, several pragmatic shortcuts were taken:
- One `stylelint-disable-next-line` comment bypasses the `z-index` ban in `live-highway.css`
- The `css-linting` spec still contains a "Stylelint compatible with Tailwind CSS v4" requirement that is now dead
- The `stylelint.config.js` still allows `@theme` in `ignoreAtRules` (Tailwind remnant)

## Goals / Non-Goals

**Goals:**
- Eliminate all `stylelint-disable` comments by fixing the underlying issues
- Eliminate `z-index` via DOM restructuring (move sticky header outside scroll container)
- Remove obsolete Tailwind references from specs and lint config
- Consolidate duplicate `@keyframes` into `utilities.css`
- Add `prefers-contrast` / `forced-colors` accessibility support

**Non-Goals:**
- Refactoring TS/CSS state separation (that's `css-state-separation`)
- Adding Container Queries, View Transitions, or other modern CSS features (that's `css-modern-patterns`)
- Redesigning visual appearance of components

## Decisions

### Decision 1: Eliminate z-index via DOM restructuring

The `z-index: 10` in `.stage-header` existed because it was a `position: sticky` sibling of `.date-separator` elements inside the same scroll container. The correct fix is to move `.stage-header` outside the scroll container entirely — it is a static column label that should not participate in the scroll area's stacking context. This eliminates the z-index, the `isolation: isolate` hack, and the hardcoded `inset-block-start: 41px` magic number on `.date-separator` (see `fix-highway-layout` change for implementation).

**Alternative considered**: `isolation: isolate` on the parent. Rejected because `isolation: isolate` only scopes children's z-index from leaking outward — it does not control sibling stacking order within the container. `position: sticky` alone (without a non-auto z-index) does not create a stacking context, so siblings with implicit stacking contexts (e.g., via `backdrop-filter`) will still paint over the header.

### Decision 2: Remove Tailwind at-rule allowances

Remove `@theme` from `ignoreAtRules` in `stylelint.config.js` and `theme()` from `ignoreFunctions`. These were needed for Tailwind v4 compatibility but serve no purpose now.

### Decision 3: Keyframes consolidation into utilities.css

Any `@keyframes` definition that appears in both a component CSS file and `utilities.css` should exist only in `utilities.css` within `@layer utility`. Component CSS files should reference the animation by name without redefining the keyframes.

## Risks / Trade-offs

- [Risk] Removing `@theme` from `ignoreAtRules` could break if any CSS file still references it → Grep codebase for `@theme` usage before removing
