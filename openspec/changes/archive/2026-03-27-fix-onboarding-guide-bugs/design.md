## Context

The onboarding guide flow has 4 bugs that share two root causes:

1. **Top-layer color inheritance break**: The Popover API promotes elements to the top-layer, which inherits styles from `<html>` (not `<body>`). The project's global CSS sets `color: var(--color-text-primary)` on `body`, but `<html>` retains the browser default `color: black`. All `bottom-sheet` text renders as black-on-dark — invisible.

2. **`data-stage` selector collision + premature spotlight**: `document.querySelector('[data-stage="home"]')` matches `page-help`'s decorative `<strong data-stage="home">` (DOM-first) instead of `concert-highway`'s structural `<span data-stage="home">`. The matched element is inside a closed bottom-sheet (0×0 rect, invisible). The spotlight anchors to this ghost, producing no visible cutout, mispositioned tooltips, and non-functional click blockers — blocking onboarding progression.

The lane intro further compounds the problem by calling `activateSpotlight()` during `attached()`, before `dateGroups` data loads and before `concert-highway` renders its stage headers (gated by `if.bind="dateGroups.length > 0"`).

## Goals / Non-Goals

**Goals:**

- Restore text readability in all bottom-sheet popovers across the app
- Ensure coach-mark always targets the correct, visible element
- Eliminate the race between data loading, DOM rendering, and spotlight activation
- Fix the progression-blocking bug so celebration always appears

**Non-Goals:**

- Redesigning the onboarding flow structure or step progression
- Changing the coach-mark's CSS Anchor Positioning approach
- Modifying backend API responses or data contracts

## Decisions

### Decision 1: Fix top-layer color at the Global CSS layer

**Choice:** Add `:where([popover], dialog) { color: var(--color-text-primary) }` to `global.css`.

**Why not fix in `bottom-sheet.css`?** The `bottom-sheet` block could add `color: var(--color-text-primary)` to its `:scope`, but this treats the symptom per-component. Every future popover/dialog would need the same fix. The CUBE CSS methodology says Global CSS should set sensible defaults so blocks don't have to repeat them. `:where()` keeps specificity at zero, so any block can override.

**Why not `color: inherit`?** In the top-layer, `inherit` resolves from `<html>`, which is `black` — the very problem we're solving.

### Decision 2: Replace `data-stage` in page-help with scoped CSS classes

**Choice:** Change `page-help.html` from `<strong class="stage-label" data-stage="home">` to `<strong class="stage-label stage-home">`. Update `page-help.css` selectors accordingly.

**Why not scope the coach-mark selector alone?** Scoping the coach-mark selector to `concert-highway [data-stage="home"]` fixes the immediate collision, but the underlying design violation remains: two unrelated components share the same `data-*` namespace for different purposes. CUBE CSS reserves `data-*` attributes for exceptions (state deviations), not decorative styling hooks. Using CSS classes for the page-help color variants is semantically correct and prevents future collisions.

**Both fixes applied:** The coach-mark selector is also scoped (Decision 4) as defense-in-depth.

### Decision 3: Use `@watch` + `queueTask` for reactive spotlight activation

**Choice:** Replace the imperative `while (isLoading) await sleep(100)` polling loop and premature `activateSpotlight()` with Aurelia 2's `@watch` decorator observing `dateGroups.length`, combined with `queueTask()` to defer spotlight activation until after DOM rendering.

**Flow redesign:**

```
needsRegion = false:
  loading()  → await loadDashboardEvents()  ← block until data ready
  attached() → startLaneIntro()
                 → queueTask(() => updateSpotlightForPhase())

needsRegion = true:
  attached() → startLaneIntro()
                 → homeSelector.open()      ← NO spotlight yet
  onHomeSelected() → loadData()             ← fire-and-forget
  @watch(dateGroups.length) → if > 0:
    → laneIntroPhase = 'home'
    → queueTask(() => updateSpotlightForPhase())
```

**Why `@watch` over `dataGroups` changed callback?** `dateGroups` is a plain array assignment (not `@observable`), so `dateGroupsChanged()` won't fire. `@watch` with an expression callback `(vm) => vm.dateGroups.length` observes the computed length reactively, including when the array reference changes.

**Why `queueTask`?** When `dateGroups` changes, Aurelia schedules template updates (including `if.bind="dateGroups.length > 0"` evaluation) in its microtask queue. `queueTask()` executes after that queue flushes, guaranteeing `[data-stage="home"]` exists in the DOM before `findAndHighlight()` searches for it.

**Why not use `loading()` hook for all cases?** The `loading()` router hook can `await` data, but only for the initial page load. The `needsRegion=true` path requires user interaction (Home Selector selection) before data can be fetched, so `loading()` cannot block on that. `@watch` elegantly handles both the initial load and the post-selection reload.

### Decision 4: Scope coach-mark target selectors to concert-highway

**Choice:** Change all lane intro spotlight selectors from `'[data-stage="home"]'` to `'concert-highway [data-stage="home"]'` (and similarly for near/away).

This is defense-in-depth alongside Decision 2. Even after removing `data-stage` from `page-help`, scoped selectors prevent future collisions if any component adds `data-stage` attributes.

## Risks / Trade-offs

- **`queueTask` timing**: `queueTask` guarantees execution after the current microtask queue, but if `if.bind` evaluation is deferred across multiple frames, the target may still be absent. Mitigation: `findAndHighlight()` already has exponential backoff retry (up to 5s). The `queueTask` just eliminates the common case; retries handle edge cases.

- **`@watch` on array length**: Aurelia's `@watch` with `vm.dateGroups.length` fires when the length changes, but also fires with `0 → 0` on reassignment of an empty array. Mitigation: the `@watch` handler checks `newLen > 0` before acting.

- **Global `:where([popover], dialog)` color rule**: Applies to all popovers/dialogs, not just bottom-sheet. This is intentional — any popover in this dark-theme app needs white text. Risk: if a future light-theme popover is added, it would need an explicit color override. Mitigation: `:where()` has zero specificity, so any block-level override wins.
