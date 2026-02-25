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

**Rationale:** Currently, components either poll services or rely on `promise.bind` for initial load only. `@watch` makes reactive dependencies explicit and eliminates manual event wiring. `@computed` with explicit deps (Beta 27) prevents unnecessary re-evaluation.

**Where NOT to apply:** Simple property access in templates (Aurelia's binding engine already handles this efficiently).

### Decision 4: View Transitions API for route animations

**Choice:** Replace the current CSS `@keyframes page-enter` animation on `au-viewport > *` with the View Transitions API.

**Rationale:** View Transitions run off the main thread, improving INP scores. They also provide cross-document transition capability for future use. The current CSS approach blocks the main thread during route changes.

**Fallback:** Keep the existing CSS animation as a fallback for browsers without View Transitions support using `@supports`.

### Decision 5: Container Queries for event card responsive layout

**Choice:** Convert `live-highway` event card grid from viewport-based to container-based responsive design.

**Rationale:** Event cards appear in a 3-lane grid. Their layout should adapt based on the lane width, not the viewport. This enables the same card component to render correctly in different contexts (highway, detail sheet, future reuse).

### Decision 6: Value converters for date/time only

**Choice:** Create a single `DateValueConverter` with format options, not a library of converters.

**Rationale:** The audit showed date formatting as the only repeated formatting concern. A single converter with a `format` parameter (`'short'`, `'long'`, `'relative'`) covers all use cases without over-engineering.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| `.class` binding with Tailwind utility classes containing colons (e.g., `md:text-lg`) may not parse correctly | Test with Tailwind's responsive/state modifiers; fall back to `class.bind` object syntax if needed |
| `@watch` could cause unexpected update cascades if watches trigger property changes that trigger other watches | Apply `@watch` conservatively; avoid watching properties that trigger other watched properties |
| View Transitions API browser support gaps | Use `@supports (view-transition-name: x)` with CSS fallback to existing keyframe animation |
| Container Queries may conflict with Tailwind v4's responsive utilities | Use `@container` in component-scoped CSS files, not inline Tailwind classes; Tailwind v4 supports `@container` natively |
| `batch()` misuse could defer updates that should be synchronous (e.g., optimistic UI) | Only apply `batch()` to service-layer bulk mutations, not to UI state transitions |
