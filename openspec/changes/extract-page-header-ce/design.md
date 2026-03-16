## Context

Three route pages (my-artists, settings, tickets) share an identical `<header class="[ page-header ]">` pattern with the same CSS block (~17 lines each): `grid-area: header`, padding, border, background, and nested `h1` typography. my-artists adds flexbox + gap for its extra action elements (count badge, view-toggle button). There is no existing `page-header` component — the pattern is copy-pasted per route.

## Goals / Non-Goals

**Goals:**

- Single source of truth for page-header markup and styles.
- Slot-based extensibility so routes can inject trailing actions without forking the component.
- Follow CUBE CSS methodology: header styles live in the component's block layer; routes only add route-specific overrides for slotted content.

**Non-Goals:**

- Back button / navigation behavior — out of scope.
- Sticky/scroll-aware header behavior — not currently used, not adding it.
- Abstracting the route-level grid layout (`grid-template-areas: "header" "main"`) — stays in each route's `:scope`.

## Decisions

### 1. Light DOM CE with `<au-slot>` (not Shadow DOM)

The header needs to participate in the parent route's CSS Grid (`grid-area: header`). Light DOM keeps this simple — no `::part()` or slot styling workarounds needed.

**Alternative considered:** Shadow DOM with `::part()` exports — rejected because the header is a layout primitive, not a style-encapsulated widget. Shadow DOM adds complexity with no benefit here.

### 2. Single `title-key` bindable + default `<au-slot>`

The CE accepts:
- `title-key` (string) — i18n key passed to `t` binding on the `<h1>`.
- Default `<au-slot>` — optional trailing content (badges, buttons).

This covers all 3 current use cases:
- settings/tickets: `<page-header title-key="settings.title"></page-header>` (no slot content)
- my-artists: `<page-header title-key="nav.myArtists"><span>...</span><button>...</button></page-header>`

**Alternative considered:** Multiple named slots (`actions`, `badge`) — rejected as over-engineering. A single default slot is sufficient; route templates already own the markup for their actions.

### 3. Flexbox layout with `h1 { flex: 1 }` as the base

The header uses `display: flex; align-items: center; gap: var(--space-3xs)`. The `<h1>` gets `flex: 1` to push any slotted actions to the end. This works for both the title-only case (settings/tickets) and the title+actions case (my-artists) without conditional styling.

### 4. Global registration in `main.ts`

Same pattern as `StatePlaceholder`, `SvgIcon`, `BottomNavBar` — globally registered CEs that are used across multiple routes.

## Risks / Trade-offs

- **Slot content styling**: Slotted elements (artist-count, toggle-view-btn) remain styled in the route's CSS. This is intentional — the CE owns the header chrome, routes own their action styling. → No mitigation needed; this follows CUBE CSS block responsibility.
- **`grid-area` coupling**: The CE's host element needs `grid-area: header` to sit in the route grid. This is handled by the CE's own CSS (`:scope { grid-area: header }`). → If a future route uses a different grid area name, it can override via the cascade.
