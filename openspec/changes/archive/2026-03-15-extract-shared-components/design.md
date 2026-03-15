## Context

Multiple route pages and components duplicate three UI patterns: inline SVG icon definitions (27+ copies across bottom-nav-bar, toast-notification, tickets-page, my-artists-page, dashboard, discover-page, settings-page, event-detail-sheet), empty/error state blocks (`.state-center` + icon + title + description in 4 pages), and page shell structure (`.page-layout` + `.page-header` + content in 5 pages). Each copy drifts slightly in sizing, spacing, or markup structure.

## Goals / Non-Goals

**Goals:**
- Extract three shared Aurelia 2 custom elements: `<svg-icon>`, `<state-placeholder>`, `<page-shell>`
- Replace all inline SVG definitions with `<svg-icon>` references
- Replace duplicated empty/error state blocks with `<state-placeholder>`
- Replace duplicated page layout boilerplate with `<page-shell>`
- Remove orphaned CSS from route stylesheets after extraction
- Maintain all existing visual behavior and test assertions

**Non-Goals:**
- Adding new icons or visual changes
- Changing page behavior or routing logic
- Extracting loading spinner patterns (still page-specific)
- Wrapping discover-page in `<page-shell>` (it uses `data-search-mode` on `<main>` for CSS state changes)

## Decisions

### 1. SVG icon centralization via switch/case template

```html
<template switch.bind="name">
  <svg case="home" ...>...</svg>
  <svg case="search" ...>...</svg>
  <!-- 27+ cases -->
</template>
```

**Why switch/case over a sprite sheet or dynamic import:** Aurelia's `switch.bind` renders only the matched case — no hidden DOM nodes, no network requests, no build tooling. The template is statically analyzable and tree-shakes naturally. The icon set is small (~30 icons) so a single template is manageable.

**Alternative considered:** External SVG sprite with `<use href>`. Rejected because it requires build-time sprite generation, complicates scoped CSS coloring (fill/stroke inheritance through shadow DOM boundaries), and adds a network request for the sprite file.

### 2. Size variants via data attribute, not CSS classes

```html
<svg-icon name="home" size="lg"></svg-icon>
<!-- Host element gets data-size="lg" -->
```

```css
:scope[data-size="lg"] { --_icon-size: 1.5rem; }
```

**Why data attributes over class names:** CUBE CSS methodology uses data attributes for state-driven variants. The `@scope (svg-icon)` block with `:scope[data-size]` selectors keeps variant logic co-located with the component scope. This avoids class name collisions and aligns with the project's existing pattern (e.g., `data-search-mode` on discover-page).

### 3. Page-shell uses au-slot for composition, not bindable content

```html
<page-shell title-key="nav.tickets">
  <template au-slot="header-actions">
    <button>Action</button>
  </template>
  <!-- default slot: page content -->
</page-shell>
```

**Why slots over bindable props for content:** Header actions vary widely between pages (buttons, toggles, counts). Passing HTML through bindable props would require unsafe innerHTML or template refs. Aurelia's `<au-slot>` provides type-safe, scoped content projection.

**Why `titleKey` as a string prop (not a slot):** Every page header has exactly one `<h1>` with an i18n key. A bindable string with `t.bind` is simpler than a slot for this uniform case.

### 4. Discover-page excluded from page-shell

The discover page binds `data-search-mode` directly on its `<main>` element to drive CSS state transitions between bubble UI and search results. Wrapping in `<page-shell>` would move `<main>` inside the component, breaking this binding.

**Alternative considered:** Adding a `data-mode` bindable to page-shell. Rejected because it introduces a page-specific concern into a shared component. The discover page's search-mode pattern is unique and does not warrant generalizing.

### 5. State-placeholder does not cover loading states

Loading spinners remain page-specific because they vary in size, animation, and surrounding context (inline vs. full-page). The `<state-placeholder>` component handles only empty and error states — the consistent pattern of icon + title + description + optional CTA.

## Risks / Trade-offs

- **DOM structure changes break selectors** → Unit tests query component instances via DI, not DOM selectors. E2E tests use data-testid attributes. Risk is low.
- **Icon additions require template edits** → Adding a new icon means adding a `case` block to svg-icon.html. This is intentional — it keeps the icon set explicit and auditable. If the icon count exceeds ~50, consider migrating to a sprite sheet.
- **Page-shell rigidity** → Pages needing non-standard layouts (e.g., discover with search-mode) must opt out entirely. This is acceptable because the standard layout covers 4 of 5 applicable routes.
