## Context

The frontend app uses a `my-app` root component with a `page-shell` intermediate wrapper in every route. This creates 8 layers of DOM nesting from the root to scrollable content. The CSS Grid `1fr` track (= `minmax(auto, 1fr)`) allows content to expand beyond `100dvh`, breaking sticky headers and internal scroll containers. Route templates use non-semantic `<div>` elements where HTML landmark elements are appropriate.

Current DOM chain (dashboard):
```
my-app → .app-viewport(div) → au-viewport → dashboard → page-shell → main.page-layout
  → .dashboard-body(div) → live-highway → .highway-layout(div) → .highway-scroll(div)
```

## Goals / Non-Goals

**Goals:**
- Flatten DOM from 8 layers to 3 layers (au-viewport → route → main)
- Fix sticky/scroll behavior structurally via `minmax(0, 1fr)` Grid tracks
- Replace non-semantic `<div>` with HTML landmark elements per web.dev/MDN guidelines
- Delete `page-shell` component — routes own their layout
- Rename `my-app` → `app-shell` to reflect its role

**Non-Goals:**
- Redesigning route-internal component architecture (e.g., `live-highway` stays as CE)
- Changing visual appearance — this is a structural refactor only
- Adding new features or modifying business logic
- Refactoring CSS methodology (CUBE CSS remains)

## Decisions

### Decision 1: app-shell provides only frame — routes own `<header>` + `<main>`

**Choice:** app-shell renders `<au-viewport>` + `<bottom-nav-bar>` + top-layer overlays. No header, no `<main>`, no page-layout wrapper.

**Why not keep page-shell in app-shell?** Headers vary significantly per route (dashboard has none, my-artists has title + count + toggle button, discover has a search bar). A shared header component would need complex slot/service injection for the varying actions. Routes defining their own `<header>` and `<main>` is simpler and matches the MDN document structure pattern.

**Why not a header service?** Adding a DI service to communicate header state across CE boundaries is over-engineering for what is fundamentally a template concern. Each route knows its own header content — let it declare it directly.

### Decision 2: `minmax(0, 1fr)` at both Grid levels

**Choice:** Both `app-shell` and `au-viewport` use `minmax(0, 1fr)` instead of `1fr`.

**Why:** `1fr` = `minmax(auto, 1fr)`. The `auto` minimum allows Grid tracks to expand beyond the container's stated `block-size` when content is taller. With `minmax(0, 1fr)`, the track never exceeds its fair share of the container, guaranteeing that `overflow-y: auto` on `<main>` creates a proper scroll container.

**Why at both levels?** Each Grid container independently resolves track sizes. Without `minmax(0, 1fr)` at the au-viewport level, route content can still push au-viewport beyond its allocated row in app-shell.

### Decision 3: Route elements as direct Grid items — no intermediate sizing

**Choice:** Route custom elements do NOT need `:scope { display: block; block-size: 100%; }`. They are Grid items of `au-viewport` and stretch automatically via `align-self: stretch` (the default).

**Why:** Removing explicit `block-size: 100%` from route elements eliminates the percentage height chain entirely. Grid stretch provides a definite size without percentage resolution. The route's `<header>` and `<main>` are direct children that participate in the route element's block flow.

### Decision 4: `div.app-viewport` wrapper removed

**Choice:** Remove the `.app-viewport` wrapper entirely. `au-viewport` becomes a direct child of `app-shell`.

**Why:** `.app-viewport` uses `display: contents` — it generates no box. It exists only as a template grouping that adds DOM depth for no layout benefit.

### Decision 5: Semantic HTML tag mapping

**Choice:** Follow web.dev accessibility structure and MDN document structure guidelines.

Each route template uses this pattern:
```html
<!-- Route template top level -->
<header class="[...]">          <!-- banner landmark (optional per route) -->
  <h1>Page Title</h1>
  <!-- actions -->
</header>
<main>                          <!-- main landmark (exactly 1 per route) -->
  <!-- page-specific content -->
</main>
<!-- top-layer elements (dialogs, popovers) -->
```

Tag mapping for content elements:

| Current `<div>` | Replacement | Condition |
|---|---|---|
| `.app-viewport` | (deleted) | Wrapper serves no purpose |
| `.dashboard-body` | (deleted) | Unnecessary nesting |
| `.dashboard-promise-slot` | (deleted) | Unnecessary nesting |
| `.highway-layout` | `<main>` | Route's main content |
| `.highway-scroll` | (none — content directly in `<main>`) | Grid row handles scroll |
| `.artist-list` | `<ul role="list">` | List of items |
| `.artist-row` | `<li>` | List item |
| `.artist-grid` | `<ul role="list">` | List of items |
| `.grid-tile` | `<li>` | List item |
| `.ticket-list` | `<ul role="list">` | List of items |
| `.ticket-card` | `<li>` | List item |
| `.search-results .results-list` | `<ul role="list">` | List of items |
| `.result-item` | `<li>` | List item |
| `.stale-banner` | `<aside>` | Supplementary info |
| `.search-bar` | `<search>` | Search landmark |
| `.settings-body` | (deleted or `<main>` directly) | Unnecessary wrapper |
| `.state-center` (loading) | `<div role="status" aria-busy="true">` | Keep div, add ARIA |

Note: `role="list"` is required on `<ul>` because Safari removes list semantics when `list-style: none` is applied (a known behavior).

### Decision 6: CSS scoping migration

**Choice:** Route CSS files change their `@scope` target. No global CSS changes needed beyond app-shell.

```css
/* Before: scoped to page-shell internals */
@scope (my-artists-page) {
  .artist-list { ... }
}

/* After: same — route scope unchanged */
@scope (my-artists-page) {
  .artist-list { ... }  /* now targets <ul> instead of <div> */
}
```

Selectors referencing `.page-layout` are removed. Layout properties (flex, overflow) move to `<main>` within each route's CSS.

## Risks / Trade-offs

**[Risk] Large changeset across all route templates** → Mitigate by executing route-by-route with `make check` after each route. Changes are mechanical (remove page-shell wrapper, add header/main, update tag names).

**[Risk] page-shell removal breaks tests** → Mitigate by searching for `page-shell` references in test files and updating selectors. Tests that query `.page-layout` or `page-shell` need selector updates.

**[Risk] Aurelia `au-viewport` may inject wrapper elements** → Verified: Aurelia 2 viewport renders route elements directly as children. No intermediate wrapper. Route custom elements become direct Grid items.

**[Risk] `role="list"` needed for Safari accessibility** → Safari strips list semantics from `<ul>` with `list-style: none`. Adding `role="list"` explicitly preserves screen reader behavior.

**[Trade-off] Routes duplicate header markup** → Accepted. Each route declares its own 2-3 line `<header>`. This is simpler than a shared component with slot injection, and matches the HTML document structure pattern where each page has its own banner.
