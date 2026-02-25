# Aurelia 2 Best Practice Audit Report

**Date:** 2026-02-25
**Target:** `liverty-music/frontend`
**Sources:** Aurelia 2 Official Docs (Beta 27), `web-app-specialist.md` guidelines

---

## Executive Summary

The frontend is a **well-structured Aurelia 2 application** that uses many modern features effectively: lazy routing, `resolve()` DI, `promise.bind`, Shadow DOM, Tailwind v4 with OKLCH, and proper lifecycle management. However, there are **significant gaps** where the app doesn't leverage Aurelia 2's latest capabilities and deviates from web-app-specialist best practices.

### Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| DI & Service Architecture | ★★★★★ | Excellent - `resolve()`, `DI.createInterface`, singletons |
| Routing | ★★★★☆ | Lazy loading, auth guards, but missing `loaded()` hook |
| Template Syntax | ★★★☆☆ | Solid basics, but missing key Aurelia 2 features |
| Reactivity | ★★☆☆☆ | Underutilized - no `@watch`, no `@computed`, no `batch()` |
| Performance | ★★★☆☆ | Missing `key.bind`, no binding mode optimization, no debounce/throttle |
| CSS/Styling | ★★★★☆ | OKLCH + Tailwind v4, but no Container Queries or `:has()` |
| Shadow DOM & Slots | ★★★★☆ | Good selective use, but `<au-slot>` opportunities missed |
| Testing | ★★★☆☆ | Good DI test patterns, but not using `createFixture` |
| Value Converters | ☆☆☆☆☆ | None used - missing opportunities |
| Binding Behaviors | ☆☆☆☆☆ | None used - missing `debounce`, `throttle`, `signal` |

---

## Category 1: Dependency Injection — ★★★★★ Excellent

### What's Done Well

- **`resolve()` function** used consistently everywhere (not legacy `@inject`)
- **`DI.createInterface`** pattern with default singleton registration across all services
- **`INode` injection** for DOM access (`resolve(INode) as HTMLElement`)
- **`AppTask`** for startup side-effects (`GlobalErrorHandlingTask`)
- **`@lifecycleHooks()`** for cross-cutting auth concern (`AuthHook`)
- **Test containers** using `DI.createContainer()` with mock registrations
- **`ILogger.scopeTo()`** for per-component log scoping

### No Issues Found

This is the strongest area of the codebase. All Aurelia 2 DI patterns are used idiomatically.

---

## Category 2: Routing — ★★★★☆ Good

### What's Done Well

- **Lazy loading** via `component: import('./path')` on all routes
- **Auth guard** via global `AuthHook` with `canLoad()` checking `data.auth`
- **Fallback route** configured for 404
- **Route params** handled in `loading()` lifecycle hook
- **`restorePreviousRouteTreeOnError`** configured per environment
- **Navigation error handling** via `au:router:navigation-error` subscription

### Gaps

| Issue | Current | Recommended |
|-------|---------|-------------|
| `loaded()` hook | Not used anywhere | Use for post-DOM-swap tasks (analytics, focus management) |
| `canUnload()` guard | Not used | Consider for forms with unsaved changes (Settings page) |
| Route title | Not set | Use `title` property on routes for document title management |
| `isBack` detection | Not used | Useful for scroll restoration on Dashboard |

### Specific Findings

**`my-app.ts` route definitions lack `title`:**
```typescript
// Current
{ path: 'dashboard', component: import('./routes/dashboard') }

// Recommended
{ path: 'dashboard', component: import('./routes/dashboard'), title: 'Dashboard' }
```

**`dashboard.ts` — no `loaded()` hook:**
The Dashboard component could benefit from `loaded()` for analytics tracking and scroll position restoration, especially since it reuses for `concerts/:id`.

---

## Category 3: Template Syntax — ★★★☆☆ Needs Improvement

### What's Done Well

- **`promise.bind`** with `pending`/`then`/`catch` (Dashboard) — excellent async pattern
- **`view-model.ref`** / `component.ref` for imperative component access
- **`<import>` statements** for local component registration
- **Custom event dispatching** and listening (`artist-selected.trigger`)
- **`aria-checked.bind`** for accessibility

### Gaps — Missing Aurelia 2 Features

#### 1. No `:` (colon) shorthand syntax
```html
<!-- Current -->
<img src.bind="qrDataUrl">
<button disabled.bind="!selectedPrefecture">

<!-- Aurelia 2 shorthand (equivalent, more concise) -->
<img :src="qrDataUrl">
<button :disabled="!selectedPrefecture">
```
**Impact:** Low — purely stylistic, but aligns with modern framework conventions.

#### 2. No `.class` binding syntax
```html
<!-- Current (string interpolation — fragile, hard to maintain) -->
class="... ${isActive(tab.path) ? 'text-brand-accent' : 'text-text-muted'}"

<!-- Aurelia 2 recommended -->
<a text-brand-accent.class="isActive(tab.path)"
   text-text-muted.class="!isActive(tab.path)">

<!-- Or with multi-class toggle (Beta 24+) -->
<a text-brand-accent,font-semibold.class="isActive(tab.path)">
```
**Impact:** Medium — string interpolation for class toggling is error-prone and harder to read.

#### 3. No `switch.bind` usage
```html
<!-- Current pattern in templates — nested if.bind chains -->
<svg if.bind="tab.icon === 'home'">...</svg>
<svg if.bind="tab.icon === 'discover'">...</svg>
<svg if.bind="tab.icon === 'artists'">...</svg>

<!-- Aurelia 2 recommended -->
<template switch.bind="tab.icon">
  <svg case="home">...</svg>
  <svg case="discover">...</svg>
  <svg case="artists">...</svg>
  <svg default-case>...</svg>
</template>
```
**Impact:** Medium — improves readability and intent clarity for multi-branch conditionals.

#### 4. No `show.bind` anywhere
All conditional rendering uses `if.bind`, which removes/re-adds DOM. For frequently toggled elements (loading spinners, toasts, bottom sheets), `show.bind` would be better:
```html
<!-- Current: if.bind destroys and recreates the element each toggle -->
<bottom-nav-bar if.bind="showNav"></bottom-nav-bar>

<!-- Better for frequently toggled UI: preserves DOM, just toggles visibility -->
<bottom-nav-bar show.bind="showNav"></bottom-nav-bar>
```
**Impact:** Medium — performance improvement for frequently toggled UI elements.

#### 5. No `<let>` element for template-local variables
```html
<!-- Current: repeated expressions in templates -->
${followedCount > 0 ? '· ' + followedCount : ''}
<!-- ... same expression used again later ... -->

<!-- Aurelia 2 recommended: compute once, reuse -->
<let formatted-count.bind="followedCount > 0 ? '· ' + followedCount : ''"></let>
${formattedCount}
```
**Impact:** Low-Medium — reduces expression duplication and improves template readability.

#### 6. No spread binding (`...$bindables`)
Some components pass many properties individually. Spread binding could simplify:
```html
<!-- Could use spread for event data passing -->
<event-card ...$bindables="eventData" lane="main">
```
**Impact:** Low — applicable in limited cases in this codebase.

#### 7. No local templates (`as-custom-element`)
Some templates contain repeated UI patterns that could be extracted into file-local templates without creating separate component files:
```html
<!-- Could define inline for repeated card patterns -->
<template as-custom-element="skeleton-card">
  <div class="animate-pulse rounded-card bg-surface-elevated h-32"></div>
</template>
```
**Impact:** Low — useful for reducing boilerplate in complex templates.

---

## Category 4: Reactivity — ★★☆☆☆ Significantly Underutilized

### Current State

- **Only `@observable`** is used, and only in one place (`ErrorBoundaryService.currentError`)
- All other state changes rely on plain property assignment with template binding
- No `@watch`, `@computed`, or `batch()` anywhere

### Missing Patterns

#### 1. `@watch` — not used anywhere
Multiple components manually subscribe to service state changes or use polling:

```typescript
// Current pattern in Dashboard
loading(params) {
  this.dataPromise = this.dashboardService.loadEvents(...)
}

// Could use @watch for reactive region changes
@watch((vm: Dashboard) => vm.dashboardService.selectedRegion)
onRegionChanged(newRegion: string) {
  this.dataPromise = this.dashboardService.loadEvents(newRegion)
}
```

**Impact:** High — `@watch` eliminates manual event wiring and makes reactive dependencies explicit.

#### 2. `@computed` — not used anywhere
Some getters could benefit from `@computed` for explicit dependency tracking:

```typescript
// Current in MyApp
get showNav(): boolean {
  const hideOnRoutes = ['welcome', 'onboarding', 'auth/callback']
  // ... complex logic
}

// With @computed (explicit deps, cached)
@computed('router.currentRoute')
get showNav(): boolean { ... }
```

**Impact:** Medium — prevents unnecessary re-evaluation of getters.

#### 3. `batch()` — not used anywhere
Several places update multiple properties in sequence:

```typescript
// Current in ArtistDiscoveryService
this.availableBubbles = [...]
this.followedArtists = [...]
this.orbIntensity = calculateIntensity(...)

// With batch() — single DOM update cycle
batch(() => {
  this.availableBubbles = [...]
  this.followedArtists = [...]
  this.orbIntensity = calculateIntensity(...)
})
```

**Impact:** Medium — reduces intermediate DOM updates when multiple properties change together.

---

## Category 5: Performance — ★★★☆☆ Needs Attention

### Critical Missing: `key.bind` on `repeat.for`

**No `repeat.for` in the entire codebase uses `key.bind`**. This is a significant performance issue for dynamic lists:

```html
<!-- Current -->
<event-card repeat.for="ev of group.main" event.bind="ev" lane="main">

<!-- Required for proper reconciliation -->
<event-card repeat.for="ev of group.main; key.bind: ev.id" event.bind="ev" lane="main">
```

**Affected locations:**
- `live-highway.html` — event cards (3 repeat.for loops)
- `my-artists-page.html` — artist list
- `area-selector-sheet.html` — city buttons
- `bottom-nav-bar.html` — navigation tabs
- `dashboard.html` — date groups

**Impact:** High — without `key.bind`, Aurelia cannot efficiently reconcile list changes. Items may lose state during reorder/filter/sort operations.

### Missing Binding Mode Optimization

All bindings use default `.bind` (auto-detect mode). For display-only data, explicit `.to-view` or `.one-time` would reduce observation overhead:

```html
<!-- Current — auto-detected as two-way on some elements -->
<span>${event.artistName}</span>  <!-- interpolation is fine -->
<img src.bind="event.imageUrl">    <!-- auto = to-view, OK -->

<!-- But for truly static data (icons, config values) -->
<icon-ticket></icon-ticket>  <!-- Already fine as custom element -->

<!-- Consider .one-time for data that never changes after initial load -->
<a href.one-time="googleMapsUrl">
```

**Impact:** Low-Medium — marginal performance gain, but good practice for large lists.

### Missing `debounce` and `throttle` Binding Behaviors

```html
<!-- Current: raw input handler fires on every keystroke -->
<input input.trigger="onSearchInput()">

<!-- Aurelia 2 recommended: debounce search -->
<input value.bind="searchQuery & debounce:300">

<!-- For touch/swipe handlers -->
<div touchmove.trigger="onTouchMove($event) & throttle:16">
```

**Impact:** Medium — prevents excessive re-renders and API calls during user input.

### No `virtual-repeat` for Long Lists

The artist list in `my-artists-page` and event lists could grow large. Consider `virtual-repeat.for` when lists exceed ~100 items.

**Impact:** Low (depends on expected data volume).

---

## Category 6: CSS/Styling — ★★★★☆ Good, Some Gaps

### What's Done Well (aligned with web-app-specialist)

- **OKLCH color system** ✅ — All theme colors use `oklch()` in `@theme`
- **Tailwind CSS v4** ✅ — Using native `@import "tailwindcss"` syntax with `@theme`
- **CSS design tokens** ✅ — Proper `--color-*`, `--font-*`, `--radius-*`, `--shadow-*` custom properties
- **`prefers-reduced-motion`** ✅ — Animation respect for accessibility
- **`shadowCSS()`** ✅ — Proper Shadow DOM styling approach

### Gaps per web-app-specialist Guidelines

| Guideline | Status | Notes |
|-----------|--------|-------|
| Container Queries (`@container`) | ❌ Not used | No responsive container-based layouts found |
| CSS Nesting | ❌ Not used | All styles are Tailwind utilities or flat CSS |
| `:has()` selectors | ❌ Not used | JS used for styling states instead |
| Anchor Positioning | ❌ Not used | Bottom sheets use JS positioning |
| Subgrid | ❌ Not used | `live-highway` grid could benefit |
| CSS Logical Properties | ❌ Not used | Physical properties (margin-top, etc.) used |
| View Transitions API | ❌ Not used | Page transitions use CSS animations on `au-viewport > *` |
| Scroll-driven Animations | ❌ Not used | Could enhance scroll-based UI elements |

### Specific Opportunities

**Container Queries** — The event card grid in `live-highway` renders in 3 lanes. Cards should adapt based on their container width, not viewport:
```css
/* Current: viewport-based responsive */
@media (min-width: 768px) { ... }

/* Recommended: container query */
.highway-lane { container-type: inline-size; }
@container (min-width: 200px) { .event-card { ... } }
```

**`:has()` for state-based styling:**
```css
/* Instead of JS toggling classes for active nav items */
.nav-item:has(.active-indicator) { color: var(--color-brand-accent); }
```

**View Transitions API** for route changes:
```css
/* Instead of CSS animation on au-viewport > * */
@view-transition { navigation: auto; }
::view-transition-old(root) { animation: fade-out 200ms; }
::view-transition-new(root) { animation: fade-in 200ms; }
```

---

## Category 7: Shadow DOM & Slots — ★★★★☆ Good

### What's Done Well

- **Selective Shadow DOM** — Only used where encapsulation is needed (artist-discovery, discover, loading-sequence)
- **`shadowCSS()` with raw imports** — Correct pattern for Shadow DOM styling
- **Light DOM** for layout components — Correct decision for BottomNavBar, LiveHighway, etc.

### Gaps

#### No `<au-slot>` usage
All content projection uses native `<slot>` (in Shadow DOM components). For Light DOM components that need content projection, `<au-slot>` would be more appropriate:
```html
<!-- au-slot allows external CSS styling of projected content -->
<au-slot name="header"></au-slot>
```

**Impact:** Low — current Shadow DOM components correctly use `<slot>`.

#### No `@slotted` or `@children` decorators
Components that observe child elements (like `BottomNavBar` tabs) could use `@children` instead of hardcoded arrays:
```typescript
// Current: hardcoded tab array in component
readonly tabs = [
  { path: 'dashboard', icon: 'home', label: 'Home' },
  ...
]

// Alternative with @children: dynamic tab discovery
@children('nav-tab') tabs: NavTab[]
```

**Impact:** Low — current hardcoded approach is simpler and appropriate.

---

## Category 8: Value Converters — ☆☆☆☆☆ Not Used

**Zero value converters in the entire codebase.** This is a significant missed opportunity.

### Recommended Value Converters to Add

| Converter | Use Case | Current Workaround |
|-----------|----------|-------------------|
| `date` | Format event dates | Inline JS in templates / service methods |
| `relativeTime` | "3 hours ago" display | Manual computation |
| `truncate` | Long artist names / descriptions | CSS `text-overflow` (OK for single line) |
| `currency` | Ticket prices | Not applicable yet |
| `json` | Debug display | Not needed in prod |

**Example — Date formatting:**
```typescript
// Instead of doing this in services/components:
formatDate(date: Date): string {
  return new Intl.DateTimeFormat('ja-JP', { ... }).format(date)
}

// Create a reusable value converter:
@valueConverter('date')
export class DateValueConverter {
  toView(value: string | Date, format = 'medium'): string {
    return new Intl.DateTimeFormat('ja-JP', { dateStyle: format }).format(new Date(value))
  }
}

// Template usage:
${event.date | date:'long'}
```

**Impact:** Medium — improves template readability and reusability of formatting logic.

---

## Category 9: Binding Behaviors — ☆☆☆☆☆ Not Used

**Zero binding behaviors (including built-in ones) are used.**

### Missing Built-in Binding Behaviors

| Behavior | Where to Apply | Impact |
|----------|---------------|--------|
| `& debounce:300` | Search inputs in `my-artists-page`, `area-selector-sheet` | Reduces unnecessary processing |
| `& throttle:16` | Touch/swipe handlers in `my-artists-page` | Prevents jank during swipe |
| `& self` | Click handlers on overlays/modals | Prevents unintended bubble handling |
| `& signal:'region-changed'` | Region-dependent bindings | Efficient cross-component refresh |
| `& oneTime` | Static config data | Eliminates observation overhead |

### Custom Binding Behavior Opportunities

**Intersection Observer behavior** — for lazy-loading event card images:
```html
<img src.bind="event.imageUrl & lazyLoad">
```

**Impact:** Medium — built-in behaviors like `debounce` and `throttle` directly improve UX.

---

## Category 10: Testing — ★★★☆☆ Adequate

### What's Done Well

- **DI-based testing** with mock services via `DI.createContainer()`
- **Mock factories** for auth, logger, and RPC clients
- **JSDOM setup** with proper Aurelia test platform

### Gaps

- **Not using `createFixture`** — Aurelia 2's official testing utility. Tests manually bootstrap containers instead.
- **No component render tests** — tests focus on service logic, not template rendering
- **No interaction tests** — no `trigger.click()`, `type()` patterns from Aurelia testing
- **No `tasksSettled()`** — for waiting on async binding updates

```typescript
// Recommended Aurelia 2 testing pattern:
import { createFixture } from '@aurelia/testing'

it('shows loading state', async () => {
  const { assertHtml, stop } = await createFixture
    .component(Dashboard)
    .deps(Registration.instance(IDashboardService, mockDashboardService))
    .build()
    .started

  assertHtml.textContains('.loading', 'Loading...')
  await stop(true)
})
```

**Impact:** Medium — `createFixture` provides more concise and idiomatic tests.

---

## Category 11: web-app-specialist Guideline Compliance

### ✅ Compliant

| Guideline | Status |
|-----------|--------|
| Direct DOM over Virtual DOM | ✅ Aurelia's native binding |
| `@customElement` usage | ✅ Used for icons, components |
| `@inject` → `resolve()` migration | ✅ Using `resolve()` exclusively |
| Lifecycle hooks | ✅ Extensive use of `binding`, `attached`, `detaching`, `unbinding` |
| `if.bind`, `repeat.for`, `<au-slot>` | ✅ (partially — no `<au-slot>`) |
| OKLCH colors | ✅ All theme tokens |
| Tailwind CSS v4 | ✅ Native syntax |
| Shadow DOM where appropriate | ✅ Selective use |
| TypeScript throughout | ✅ Strict typing |

### ❌ Non-Compliant

| Guideline | Expected | Actual |
|-----------|----------|--------|
| Container Queries | Use `@container` for responsive layout | Only `@media` viewport queries |
| CSS Nesting | Use native CSS nesting | Flat CSS / Tailwind only |
| `:has()` selectors | Reduce JS for styling states | JS class toggling |
| Anchor Positioning | CSS-based positioning for tooltips/sheets | JS-based positioning |
| CSS Logical Properties | `margin-inline`, `padding-block` etc. | Physical `margin-top`, `padding-left` |
| View Transitions API | Route change animations | CSS animation on `au-viewport > *` |
| Scroll-driven Animations | Offload scroll animations | Not used |
| Modern State Management (Signals/Fine-grained reactivity) | `@watch`, `@computed`, `batch()` | Plain property assignment only |
| `switch/case` in templates | Multi-branch conditionals | Chained `if.bind` |

---

## Priority Recommendations

### P0 — Critical (Performance/Correctness)

1. **Add `key.bind` to all `repeat.for`** — prevents DOM reconciliation bugs and state loss
2. **Add `& debounce` to search inputs** — prevents excessive processing
3. **Use `show.bind` for frequently toggled elements** — avoids unnecessary DOM destruction

### P1 — High (Best Practice Alignment)

4. **Introduce `@watch`** for reactive cross-property observation (replace manual event wiring)
5. **Introduce `@computed`** for expensive getters
6. **Use `batch()`** where multiple properties change together
7. **Create value converters** for date/time formatting (reusable, testable)
8. **Add route `title` properties** for document title management
9. **Use `.class` binding syntax** instead of string interpolation for class toggling

### P2 — Medium (Modern Web Platform)

10. **Adopt Container Queries** for component-level responsive design
11. **Adopt View Transitions API** for route change animations
12. **Use `:has()` selectors** to reduce JS-based style toggling
13. **Use `switch.bind`** for multi-branch conditionals
14. **Migrate to `createFixture`** for component tests

### P3 — Low (Polish)

15. **Explore `:` shorthand syntax** for cleaner templates
16. **Add `& throttle` to touch handlers**
17. **Consider `<let>` elements** for complex template expressions
18. **Add `<au-slot>`** where Light DOM content projection is needed
19. **Explore `$previous`** in repeat.for for section header rendering (Beta 27)
20. **Adopt CSS Logical Properties** for internationalization readiness

---

## Architecture Diagram — Current vs. Recommended

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│  │Component │───▶│ Service  │───▶│ RPC/API  │                 │
│  │          │    │(Singleton│    │(Connect) │                 │
│  │ Plain    │    │ State)   │    │          │                 │
│  │ Props    │    │          │    │          │                 │
│  └──────────┘    └──────────┘    └──────────┘                 │
│       │                                                        │
│       ▼                                                        │
│  Template: .bind, if.bind, repeat.for, promise.bind            │
│  CSS: Tailwind v4 + OKLCH (@theme) ✓                          │
│  Missing: @watch, @computed, batch(), key.bind, debounce       │
│  Missing: Container Queries, View Transitions, :has()          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

                          ║
                          ▼

┌─────────────────────────────────────────────────────────────────┐
│                 RECOMMENDED ENHANCEMENTS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│  │Component │───▶│ Service  │───▶│ RPC/API  │                 │
│  │          │    │(Singleton│    │(Connect) │                 │
│  │ @watch   │    │ @observ  │    │          │                 │
│  │ @computed│    │ batch()  │    │          │                 │
│  └──────────┘    └──────────┘    └──────────┘                 │
│       │                                                        │
│       ▼                                                        │
│  Template:                                                     │
│    + key.bind on repeat.for                                    │
│    + switch.bind for multi-branch                              │
│    + show.bind for frequent toggles                            │
│    + .class binding syntax                                     │
│    + & debounce / & throttle behaviors                         │
│    + value converters (date, relativeTime)                     │
│                                                                │
│  CSS:                                                          │
│    + @container queries (component-level responsive)            │
│    + View Transitions API (route animations)                   │
│    + :has() selectors (state-based styling)                    │
│    + CSS Logical Properties (i18n readiness)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## File-by-File Findings Index

| File | Issues |
|------|--------|
| `src/my-app.ts` | Missing route `title` props |
| `src/my-app.html` | `if.bind` → `show.bind` for `bottom-nav-bar` |
| `src/components/live-highway/live-highway.html` | Missing `key.bind` on 3 repeat.for loops |
| `src/components/live-highway/event-card.html` | String interpolation for class toggling → `.class` |
| `src/components/bottom-nav-bar/bottom-nav-bar.html` | Chained `if.bind` → `switch.bind` for icons |
| `src/components/area-selector-sheet/area-selector-sheet.html` | Missing `key.bind`, no `& debounce` on search |
| `src/routes/my-artists/my-artists-page.html` | Missing `key.bind`, no `& throttle` on swipe, no `& debounce` on search |
| `src/routes/dashboard.ts` | No `@watch` for region changes, no `loaded()` hook |
| `src/routes/dashboard.html` | Missing `key.bind` on dateGroups repeat |
| `src/routes/tickets/tickets-page.html` | Minor: could use `.class` binding |
| `src/services/artist-discovery-service.ts` | Multiple property updates → `batch()` |
| `src/services/error-boundary-service.ts` | Good `@observable` usage (only instance) |
| `src/my-app.css` | No Container Queries, no View Transitions, no CSS Logical Properties |
| All `*.css` files | No CSS nesting, no `:has()` selectors |

---

*Report generated by OpenSpec Explore mode. This is analysis only — no code changes were made.*
*To begin implementing these recommendations, use `/opsx:new aurelia-best-practice` or `/opsx:ff aurelia-best-practice`.*
