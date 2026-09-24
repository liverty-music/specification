## Context

The Liverty Music frontend is built with Aurelia 2 (latest), Tailwind CSS v4, and TypeScript. An audit (see `research/aurelia-audit-report.md`) found that while the DI architecture is exemplary, the codebase underutilizes Aurelia 2's reactivity system, template features, and modern CSS platform capabilities. The app currently works correctly but leaves performance and maintainability gains on the table.

Current state:
- Zero `@watch`, `@computed`, `batch()` usage — state flows through plain property assignment
- Zero value converters or binding behaviors (including built-in `debounce`/`throttle`)
- All `repeat.for` loops lack `key.bind`
- Class toggling uses fragile string interpolation instead of `.class` binding
- CSS relies on `@media` viewport queries only; no Container Queries or View Transitions

## Goals / Non-Goals

**Goals:**
- Adopt Aurelia 2 reactivity primitives (`@watch`, `@computed`, `batch()`) where they provide clear value
- Fix all `repeat.for` loops with `key.bind` for correct DOM reconciliation
- Introduce binding behaviors (`debounce`, `throttle`) for input handling
- Create reusable value converters for date formatting
- Adopt modern CSS features (Container Queries, View Transitions API) per web-app-specialist guidelines
- Replace template anti-patterns (chained `if.bind` → `switch.bind`, string interpolation → `.class`)
- Use `show.bind` for frequently toggled elements

**Non-Goals:**
- Rewriting component architecture or service layer (DI patterns are already excellent)
- Migrating to a different state management library
- Adding Shadow DOM to components that currently use Light DOM
- SSR or AOT compilation (future Aurelia features not yet stable)
- Introducing `virtual-repeat` (current list sizes don't warrant it)
- Full test suite rewrite to `createFixture` (can be done incrementally later)

## Decisions

### Decision 1: Phased rollout — Templates first, then Reactivity, then CSS

**Choice:** Apply changes in three distinct phases rather than all at once.

**Rationale:** Template changes (`key.bind`, `switch.bind`, `.class`, `show.bind`, binding behaviors) are low-risk, high-impact, and mechanically verifiable. Reactivity changes (`@watch`, `@computed`) require understanding component data flow. CSS platform changes require visual testing.

**Alternatives considered:**
- All at once: Higher risk of regressions, harder to review
- Per-component: Too granular, loses the benefit of consistent patterns

### Decision 2: `.class` binding over dynamic class interpolation

**Choice:** Replace `${condition ? 'class-a' : 'class-b'}` patterns with Aurelia 2 `.class` binding syntax.

**Rationale:** `.class` binding is type-safe, avoids string concatenation bugs, and is the idiomatic Aurelia 2 pattern. Multi-class toggle syntax (Beta 24+) handles the common pattern of toggling multiple Tailwind classes on one condition.

**Example migration:**
```html
<!-- Before -->
class="${isActive(tab.path) ? 'text-brand-accent font-semibold' : 'text-text-muted'}"

<!-- After -->
<a text-brand-accent.class="isActive(tab.path)"
   font-semibold.class="isActive(tab.path)"
   text-text-muted.class="!isActive(tab.path)">
```

### Decision 3: `@watch` for cross-service reactive flows, `@computed` for expensive getters

**Choice:** Use `@watch` when a component needs to react to service state changes. Use `@computed` for getters that derive from multiple properties and are referenced in templates.

**Rationale:** Currently, components either poll services or rely on `promise.bind` for initial load only. `@watch` makes reactive dependencies explicit and eliminates manual event wiring. `@computed` (parameterless in Aurelia 2, automatic dependency tracking) prevents unnecessary re-evaluation.

**Where NOT to apply:** Simple property access in templates (Aurelia's binding engine already handles this efficiently).

### Decision 4: View Transitions API for route animations

**Choice:** Replace the current CSS `@keyframes page-enter` animation on `au-viewport > *` with the View Transitions API.

**Rationale:** View Transitions run off the main thread, improving INP scores. They also provide cross-document transition capability for future use. The current CSS approach blocks the main thread during route changes.

**Fallback:** Keep the existing CSS animation as a fallback for browsers without View Transitions support using `@supports`.

The transition styles target the `::view-transition-old(root)` and `::view-transition-new(root)` pseudo-elements, with duration and easing driven by the `--transition-route-duration` and `--transition-route-easing` design tokens rather than hardcoded values. The keyframe fallback is gated behind `@supports not (view-transition-name: x)` so only one animation path is ever active. Because the transition is decorative, it is suppressed under `prefers-reduced-motion: reduce`.

### Decision 5: Container Queries for event card responsive layout

**Choice:** Convert `live-highway` event card grid from viewport-based to container-based responsive design.

**Rationale:** Event cards appear in a 3-lane grid. Their layout should adapt based on the lane width, not the viewport. This enables the same card component to render correctly in different contexts (highway, detail sheet, future reuse).

The lane wrapper declares `container-type: inline-size`, and card layout rules live in `@container` blocks keyed to the design system's breakpoint tokens (`--container-sm`, `--container-md`, `--container-lg`), so any component wrapped the same way gets consistent breakpoints. Container-specific rules are gated behind `@supports (container-type: inline-size)`, falling back to a default single-column layout in unsupported browsers.

### Decision 6: Value converters for date/time only

**Choice:** Create a single `DateValueConverter` with format options, not a library of converters.

**Rationale:** The audit showed date formatting as the only repeated formatting concern. A single converter with a `format` parameter (`'short'`, `'long'`, `'relative'`) covers all use cases without over-engineering.

### Decision 7: `:has()` selectors over JavaScript class toggling for parent-state styling

**Choice:** Where a parent element's style depends on the state of a child or sibling, express it with a `:has()` selector instead of toggling a class from the component's view-model.

**Rationale:** `:has()` keeps state-derived styling declarative and colocated with the CSS it affects — a navigation item's active-indicator state (`:has(.active-indicator)` / `:has([aria-current])`) or a form field's invalid state (`:has(:invalid)` / `:has([aria-invalid="true"])`) no longer needs JS to reach into the DOM and flip a parent class.

### Decision 8: CSS Logical Properties for spacing and layout

**Choice:** Write new spacing, border, and positioning rules with logical properties (`margin-inline`, `margin-block`, `padding-inline`, `padding-block`, `border-inline-start`, `inset-inline`) instead of physical equivalents (`margin-left`, `margin-top`, etc.).

**Rationale:** Logical properties keep the layout internationalization-ready without a separate RTL stylesheet. Existing physical-property rules are migrated opportunistically, only when the file is already being touched for another reason, rather than as a dedicated sweep.

### Decision 9: `batch()` for multi-property service mutations

**Choice:** Service methods that mutate three or more template-bound properties in one logical operation wrap those mutations in `batch(() => { ... })`.

**Rationale:** Without batching, each property assignment triggers its own DOM update cycle; `batch()` coalesces them into a single render. Optimistic UI updates that need immediate visual feedback (e.g., a follow/unfollow toggle) are deliberately excluded from batching — only the subsequent server-confirmed rollback of the multi-property restore uses it.

### Decision 10: `@observable` for imperative side-effect properties

**Choice:** Properties whose changes must trigger an imperative side effect (error display, analytics) use the `@observable` decorator with a `<propertyName>Changed(newValue, oldValue)` handler, rather than folding the side effect into the property's setter or a watcher.

**Rationale:** Keeping the side effect in the dedicated changed-handler keeps it out of the property's core assignment path and makes it obvious the handler should perform only the side effect — not further state mutations that could cascade into other observers.

### Decision 11: `key.bind` on every `repeat.for`

**Choice:** Every `repeat.for` directive includes a `key.bind` expression pointing at a stable unique identifier for the item (e.g., `ev.id`, `tab.path`).

**Rationale:** Without a key, Aurelia's list diffing can misattribute DOM nodes to the wrong item when the list is reordered, added to, or filtered, producing subtle rendering bugs. A stable key lets the renderer reconcile by identity instead of position.

### Decision 12: `switch.bind` for three-or-more-branch conditionals on the same expression

**Choice:** Once a template chains three or more `if.bind` checks against the same expression (e.g., icon selection by `tab.icon`), it's rewritten as `switch.bind` with `case` attributes and a `default-case` fallback.

**Rationale:** Chained `if.bind` re-evaluates every branch on every change; `switch.bind` evaluates the expression once and mirrors the intent of a multi-branch selection more directly than a chain of independent conditionals.

### Decision 13: `show.bind` for elements that toggle more than once per session

**Choice:** UI elements expected to toggle visibility more than once per average session — the bottom nav bar, loading skeletons — use `show.bind` instead of `if.bind`.

**Rationale:** `if.bind` destroys and recreates the element's DOM (and any Aurelia bindings/state) on every toggle; `show.bind` just switches `display`, preserving DOM state across the frequent toggles these elements see.

### Decision 14: Debounce the API-triggering path, never the immediate UI feedback

**Choice:** For search inputs, separate the immediate UI feedback (entering search mode, pausing animations) from the expensive operation. Only the expensive call is debounced, via `& debounce:300`; inputs with no immediate UI side effect (e.g., `area-selector-sheet`) can debounce the whole binding.

**Rationale:** Debouncing the entire binding on an input with immediate UI feedback would make that feedback feel laggy. Splitting the two concerns keeps perceived responsiveness high while still avoiding excessive API calls — 300ms is enough to skip intermediate keystrokes without feeling unresponsive.

### Decision 15: `& throttle:16` on continuous event handlers

**Choice:** Handlers for continuous interactions — touch move, scroll, resize — use the `& throttle` binding behavior at one frame (`16`ms at 60fps), e.g. the swipe gesture handling in `my-artists-page`.

**Rationale:** Continuous events can fire far more often than the UI can usefully redraw; throttling to one update per frame caps handler invocations to what the display can actually show without dropping perceptible responsiveness.

### Decision 16: Route `title` on every route definition

**Choice:** Every route definition carries a `title` property, including a fallback title for the not-found route.

**Rationale:** Aurelia's router uses this to manage `document.title` on navigation, so each route change gives the browser tab/history entry a meaningful label (e.g., "Dashboard - Liverty Music") instead of a static default.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| `.class` binding with Tailwind utility classes containing colons (e.g., `md:text-lg`) may not parse correctly | Test with Tailwind's responsive/state modifiers; fall back to `class.bind` object syntax if needed |
| `@watch` could cause unexpected update cascades if watches trigger property changes that trigger other watches | Apply `@watch` conservatively; avoid watching properties that trigger other watched properties |
| View Transitions API browser support gaps | Use `@supports (view-transition-name: x)` with CSS fallback to existing keyframe animation |
| Container Queries may conflict with Tailwind v4's responsive utilities | Use `@container` in component-scoped CSS files, not inline Tailwind classes; Tailwind v4 supports `@container` natively |
| `batch()` misuse could defer updates that should be synchronous (e.g., optimistic UI) | Only apply `batch()` to service-layer bulk mutations, not to UI state transitions |
