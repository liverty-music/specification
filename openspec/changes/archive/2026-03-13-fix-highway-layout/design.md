## Context

The `live-highway` component renders a three-lane concert schedule (HOME / NEAR / AWAY). The current DOM places the stage header inside the scroll container alongside date separators — both using `position: sticky`. This structural decision created a cascade of CSS hacks: `z-index: 10` to prevent date separators painting over the header, `inset-block-start: 41px` hardcoded to offset below the header, and `isolation: isolate` to scope the z-index. All three are anti-patterns that the CSS redesign initiative aims to eliminate.

The parent `.highway-layout` uses `display: flex; flex-direction: column`, which is incorrect for a 2D structure-first layout (fixed header row + flexible scroll area) per the web-design-specialist layout engine selection principle.

## Goals / Non-Goals

**Goals:**
- Eliminate z-index, magic numbers, and isolation hacks through DOM restructuring
- Apply correct layout engine (Grid for 2D structure-first)
- Correct the flawed stacking context management rule in the css-linting spec
- Fix the incorrect reasoning in the css-cleanup design document

**Non-Goals:**
- Redesigning the visual appearance of the highway component
- Changing the three-lane grid structure or event card layout
- Modifying the date grouping logic in TypeScript
- Adding new CSS features (Container Queries, Scroll-driven Animations, etc.)

## Decisions

### Decision 1: Move stage header outside scroll container

The stage header is a static column label — it never changes based on scroll position. Placing it outside `.highway-scroll` eliminates the sticky sibling stacking conflict entirely.

**Before:**
```
.highway-scroll
  ├── .stage-header (sticky, z-index: 10)
  └── dateGroups
      ├── .date-separator (sticky, top: 41px)
      └── .lane-grid
```

**After:**
```
.highway-layout
  ├── .stage-header (static)
  └── .highway-scroll
      └── dateGroups
          ├── .date-separator (sticky, top: 0)
          └── .lane-grid
```

**Alternative considered:** Keep the header inside the scroll container and use a design token `--stage-header-height` instead of `41px`. Rejected because this only addresses the magic number, not the structural problem (sticky sibling stacking, z-index dependency). The root cause is the DOM structure.

### Decision 2: Convert highway-layout from Flexbox to Grid

`.highway-layout` manages a 2D structure: a fixed-height header row and a flexible scroll area. Per the layout engine selection table:

| Engine | Dimension | Sizing Driver | Applies here? |
|--------|-----------|---------------|---------------|
| Flexbox | 1D | Content-first | No — this is 2D |
| **Grid** | **2D** | **Structure-first** | **Yes — fixed row + flexible row** |

```css
.highway-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    block-size: 100%;
}
```

`auto` sizes the header to its content. `1fr` gives the remaining space to the scroll area. No `flex: 1` or `flex-direction: column` needed.

### Decision 3: Add scrollbar-gutter for column alignment

When `.highway-scroll` has overflow, the scrollbar narrows its content area. The `.stage-header` (now outside the scroll container) occupies the full parent width, causing a subtle column misalignment between header and grid.

`scrollbar-gutter: stable` reserves space for the scrollbar even when content doesn't overflow, keeping column widths consistent.

### Decision 4: Correct the css-cleanup design reasoning and spec rule

The `css-cleanup` change introduced an incorrect rule: "Components SHALL manage stacking via `isolation: isolate` on parent containers instead of arbitrary z-index values." This is based on two wrong premises:
1. `position: sticky` does not create a stacking context by itself (only with non-auto z-index)
2. `isolation: isolate` on a parent does not control sibling stacking order — it only scopes children's z-index from leaking outward

The correct principle: eliminate the need for z-index through proper DOM structure (don't make elements that need different stacking be sticky siblings). Remove the incorrect spec rule and fix the design document reasoning.

## Risks / Trade-offs

- [Column alignment with overlay scrollbars] → `scrollbar-gutter: stable` always reserves scrollbar space, which wastes ~15px on platforms that use overlay scrollbars (macOS). Acceptable for this component's narrow lane columns. If problematic later, `scrollbar-gutter: stable both-edges` can balance visually.
- [Existing unit/E2E tests] → Tests reference DOM structure via class selectors (`.stage-header`, `.highway-scroll`). The class names don't change, only the DOM nesting. Tests querying `.highway-scroll .stage-header` will need updating. Minimal blast radius.
