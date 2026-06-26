## Context

In Aurelia 2 the router awaits a routed component's `loading()` (the `load` hook) before running that component's activation lifecycle (`binding` → `bound` → `attaching` → `attached`) and swapping the view in. The navigation order is `canUnload(old) → canLoad(new) → unloading(old) → loading(new) → component lifecycle`. Therefore any `await` of network/RPC work inside `loading()` holds the transition: the outgoing view stays mounted (visually frozen) until the fetch resolves.

Three bottom-nav menu-tab routes do exactly this today:

- `my-artists-route.ts:68` — `await this.followStore.listFollowed(signal)`
- `dashboard-route.ts:184` — `await this.loadData()` (region-set branch; the `needsRegion` branch already fire-and-forgets via `void`)
- `discovery-route.ts:150` — `await this.bubbles.loadInitialArtists(...)`

Each route already owns an `isLoading` flag plus spinner/empty/error UI, but the view never attaches in time to show them. The Dashboard `needsRegion` branch already demonstrates the desired non-blocking shape and relies on a `@watch` handler to react when data arrives.

Constraints: frontend-only; no proto/RPC/backend change; must follow the `aurelia-reactivity` capability (`@watch`/`@observable`/`@computed`, direct mutation, no React-style state replacement).

## Goals / Non-Goals

**Goals:**
- Menu-tab view attaches immediately on tap; existing spinner/empty/error UI carries the in-flight experience.
- Data streams in afterward and renders order-independently (before or after attach).
- Data-ready side effects (Dashboard celebration + onboarding-completion latch) keep firing only once data is genuinely present, using observation rather than `attached()` timing.
- Route unit tests assert asynchronously in a deterministic, non-flaky way.

**Non-Goals:**
- No caching / stale-while-revalidate. A `FollowStore` TTL cache (mirroring `ConcertStore.listByFollower`) that would make repeat visits instant is deliberately out of scope and tracked separately. This change removes the *freeze*, not the *per-visit spinner*.
- No changes to celebration/onboarding requirements themselves — only the mechanism that detects "data is ready".
- No router configuration changes (`transitionPlan`, viewports) — default behavior is sufficient.

## Decisions

### Decision 1: Fire-and-forget the fetch from `loading()`, keep the synchronous prelude inside it
Extract each route's fetch body into a dedicated method that returns a `Promise` (`loadArtists(signal)`, the existing `loadData()`, `loadInitialBubbles()`), then call it with `void` from `loading()`. The synchronous prelude — `isLoading = true`, `new AbortController()`, URL filter restoration, guest hydrate, banner flags — stays in `loading()` before the `void` call so first paint is correct.

- **Why over moving the fetch into `attached()`**: keeping the abort/prelude colocated in `loading()` preserves a single setup site and sets `isLoading`/filters before the first render. `attached()` runs after first paint, so prelude state placed there would render one frame late. The `void`-in-`loading()` form also matches the precedent already in the Dashboard `needsRegion` branch.
- **Why return a `Promise` from the extracted method**: production calls it as `void`, but tests can `await sut.loadArtists()` deterministically (see Decision 4).

### Decision 2: Re-anchor Dashboard data-ready side effects to observed data arrival
Today `attached()` calls `onTimetableReady()` (→ `maybeCelebrate()` + `maybeFinishOnboarding()`) on the assumption, stated in the code's own comments, that "data was already awaited in `loading()`" so the timetable is real. Making the region-set branch non-blocking breaks that assumption: `attached()` would now run while the timetable is still a spinner, so confetti could fire over a loading screen and the completion latch could read not-yet-loaded engagement data.

Re-anchor `onTimetableReady()` to fire when the loaded data is **observed to arrive**, via Aurelia `@watch` (or an `@observable` readiness flag) on the data the celebration/latch implicitly depend on. This keeps both arrival paths (`loading()`-driven and `onHomeSelected()`-driven) consistent and removes the `attached()`-timing dependency entirely.

- **Why over the simpler "just `void` it and leave `onTimetableReady()` in `attached()`"** (the literal issue text): that only checks whether the callbacks *read* `dateGroups`; it ignores the stated invariant that they run "once the timetable is real". Observation enforces the real precondition instead of relying on a now-false ordering coincidence.
- **Why over the router `loaded()` hook**: `loaded()` runs right after `attached()`, still before the `void` fetch settles, so it does not solve the ordering problem. Observation does.
- **Why `@watch` over imperatively calling `onTimetableReady()` from `loadData()`'s `finally`**: observation is the Aurelia-native reactivity model and matches the existing `needsRegion` + `@watch` pattern and the `aurelia-reactivity` capability; a manual call from `finally` reintroduces imperative ordering. Guard the handler so it latches once and never fires while `needsRegion`/`isLoading` indicate the timetable is not real.

### Decision 3: Rely on existing order-independence for Discovery and re-instate abort-first
Discovery's canvas seeds artists from both `artistsChanged` (guarded by `!this.ctx`) and its `attached()` seed, so bubbles render whether data arrives before or after attach — no new ordering code needed; keep the onboarding hydrate prelude before the fetch.

For My Artists, mirror `loadData()`'s `abortController?.abort()`-before-create pattern in the extracted `loadArtists`. With the default `transitionPlan`, re-tapping the same tab is a no-op (`'none'`) and different tabs are fresh `'replace'` instances, so concurrent re-entry is unlikely — this is defensive consistency, not a known live bug. Abort placement follows the documented hook usage (`unbinding()`/`detaching()` already abort on deactivation).

### Decision 4: Deterministic async tests, not timer draining
Because `loading()` now resolves before the fire-and-forget fetch settles, tests that assert populated state right after `await sut.loading()` must change. Prefer awaiting the extracted method directly (`await sut.loadArtists()`) for data assertions, and use Aurelia's official `tasksSettled()` to flush scheduled DOM updates before asserting rendered output. Avoid open-ended microtask/timer draining (`vi.runAllTimersAsync()` as the primary mechanism), which is the historical source of flaky route specs.

- Affected specs: `test/routes/my-artists-route.spec.ts` (largest surface — `loading` suite + `beforeEach(await sut.loading())` suites), `test/routes/discovery-route.spec.ts` (fake timers), `test/routes/dashboard-route.spec.ts` (mostly synchronous `needsRegion`/banner assertions; add coverage for the `@watch`-gated celebration ordering).

## Risks / Trade-offs

- **Per-visit spinner flash** → Without a cache, every tab visit re-fetches and flashes the skeleton; for fast RPCs this can feel busier than the old brief freeze. Mitigation: accept for this change (freeze removal is the goal); fast-follow with the `FollowStore` TTL cache for stale-while-revalidate instantness.
- **Celebration regression if observation guard is wrong** → A mis-scoped `@watch` could fire the celebration twice, over a spinner, or not at all. Mitigation: one-shot latch guards already exist (`postSignupShown`, `celebrationShown`); add explicit `!needsRegion && !isLoading && data-present` guard and unit-test both arrival paths.
- **Stale late response overwriting newer state** → Non-blocking fetches raise re-entrancy odds. Mitigation: abort-first in the extracted load method + `AbortError` swallowing (Decision 3).
- **Test flakiness if `tasksSettled()` is misapplied** → `tasksSettled()` flushes the Aurelia scheduler, not arbitrary promises. Mitigation: await the extracted fetch method for data assertions; use `tasksSettled()` only for post-data DOM-render assertions.

## Migration Plan

Pure frontend refactor, no data/schema migration. Ship in one frontend PR; verify with `make test` (three route specs) + `make lint`, and manual rapid tab-switching (new frame + spinner appears immediately, data fills in, no frozen outgoing screen). Rollback is a straight revert — no persisted state or API surface changes.

## Open Questions

- Should the `FollowStore` TTL cache be pulled into this change (eliminating the per-visit spinner) or stay a separate fast-follow? Current proposal keeps it separate to bound scope; revisit if the spinner flash tests poorly in manual verification.
