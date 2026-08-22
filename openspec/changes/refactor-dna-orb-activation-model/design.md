## Context

See proposal.md — Why. The orb spans an Aurelia component (`dna-orb-canvas.ts`), a plain renderer class (`orb-renderer.ts`), and a pure stage-parameter function (`stage-effects.ts`). Key current wiring, confirmed in code and reviewed for Aurelia 2 correctness:

- `pulse()` (the celebratory flash + strobe + staggered shockwaves) is called **only** from `followedCountChanged` (`dna-orb-canvas.ts`), i.e. a `@bindable` state observer.
- `setFollowCount()` (persistent stage level: `baseIntensity`, `stageParams`, `orbRadius`, plus the physics orb-zone and comet-trail flag) is also called **only** from `followedCountChanged` — never at init.
- `followedCount` is bound from `discovery-route.ts` (`get followedCount => followStore.followedCount`); the router `loading()` hook hydrates guest follows **before** the canvas binds.
- Aurelia 2 does **not** invoke `[prop]Changed` for the value present at initial bind (framework contract) — so a hydrated guest binds at N and the stage is never applied.
- The canvas defers renderer init: `attached()` awaits `initWhenSized()` (a `ResizeObserver` wait) because the element can attach at 0×0 on SPA re-entry; `orbRenderer.init()` runs inside that await.
- `onAbsorbComplete(hue)` already runs on the true follow-gesture landing and unifies `injectColor` + gated `spawnShockwave` + `playLanding`. It is reachable only from the two absorption paths (bubble tap, search follow) — never from unfollow, migration, hydration, or rollback.

## Goals / Non-Goals

**Goals:**
- Make stage level a silent, idempotent function of the current count, applied on entry and on every change.
- Make the celebration a one-shot fired only from a real follow absorption.
- Ease stage transitions on the render loop; stop resetting transient state on a level apply.

**Non-Goals:**
- Changing `getStageParams` values or the `festival-orb-effects` contract.
- Re-tuning the zero-follow baseline aesthetics beyond removing the spurious activation (any further "how dim" tuning is a separate visual change).
- Modeling the gesture as a route-level event/callback (kept canvas-internal — see D3).

## Decisions

### D1: Split `setFollowCount` into a silent, idempotent `applyLevel`

Rename `setFollowCount(n)` → `applyLevel(n)`. It recomputes `stageParams = getStageParams(n)`, sets **target** values for continuous quantities (`baseIntensity`, `orbRadius`), and folds in the currently-in-`followedCountChanged` physics calls (`updateOrbZone`, `cometTrailEnabled`). It MUST NOT wipe particle trails (the current trail reset is transient-state destruction and breaks idempotency). `followedCountChanged(n)` becomes exactly `applyLevel(n)` — no `pulse()`.

- **Alternative — keep snap writes:** rejected; snapping plus trail-wipe is what couples transient and persistent state and causes visible hitches on rapid follows.

### D2: Seed the stage level after async size-init, reading the latest count

Insert `this.applyLevel(this.followedCount)` in `attached()` **after** `await this.initWhenSized()` and the `if (this.detached) return` guard, immediately before `physics.addBubbles(...)`. This is the async-safe analogue of Aurelia's documented "manual initial call" idiom (`bound() { this.xChanged(this.x, undefined) }`), relocated because the renderer is not initialized until after the size wait. Reading `this.followedCount` **after** the await captures any change that landed during the wait; idempotency makes a later `followedCountChanged` apply harmless.

- **Alternative — seed in `bound()`/`binding()`:** rejected; runs before `orbRenderer.init()`, writing into an uninitialized renderer.
- **Alternative — a bindable `set:`/coercion:** rejected; abusing a setter for side effects is an anti-pattern and does not solve initial application.

### D3: Keep the celebration canvas-internal, fired from `onAbsorbComplete`

Add a private `celebrate(hue)` unifying `pulse()` (made private) + `injectColor` + gated `spawnShockwave` + `playLanding` on one frame; call it only from `onAbsorbComplete`. This co-locates the whole same-frame burst at the true "gesture landed" moment and structurally eliminates the misfire: unfollow/migrate/hydrate/rollback provably never reach `onAbsorbComplete` (only the tap and search-follow absorption paths do). It also fixes today's timing skew — `follow()` flips the count immediately (optimistic) while absorption lands later, so a count-observer flash preceded the bubble's arrival.

- **Alternative — a route-level `@bindable` gesture callback from `discovery-route`:** rejected; the route would have to re-derive absorption-completion timing the canvas already owns.

### D4: Ease continuous quantities on the existing rAF loop, not per-call

`applyLevel` sets `targetBaseIntensity`/`targetOrbRadius`; the existing `orbRenderer.update(delta)` eases current→target each frame (same pattern already used for `pulseIntensity`/`swirlIntensity` decay). Do NOT start a timer/rAF per `applyLevel` call — rapid successive follows would stack tweens. Easing on the loop makes rapid follows collapse naturally to the latest target and keeps all animation off Aurelia's binding/task queue.

## Risks / Trade-offs

- **[A follow lands while the canvas is still 0×0 (pre-init)]** → `followedCountChanged` runs `applyLevel` against an uninitialized renderer (harmless no-op); the D2 post-await seed re-applies with the current count against the initialized renderer. Paths converge; no lost update, no double count.
- **[Color palette not restored on re-entry]** → `OrbRenderer` is re-`new`ed per component, so `colorPalette` starts empty on SPA re-entry; the seed restores stage geometry but not prior hues. Correct by design (color is gesture-driven, concern C); noted so reviewers don't expect hue restoration.
- **[Getter-backed bindable observation cost]** → `followedCount` is a getter over an `@observable`; propagation is via Aurelia's task queue, so `applyLevel` on the mutation path may run a microtask after `follow()` returns. Fine for a continuous rAF paint, and the reason the seed reads the value directly rather than assuming the observer already ran.
- **[Behavior change: unfollow now eases the stage down]** → Previously the snap already dropped intensity on any recompute; easing is a visual refinement, not a regression.

## Migration Plan

- Pure frontend deploy; no data migration, no proto/BSR. Standard frontend release path.
- Rollback: revert the frontend change; the orb returns to the prior observer-driven activation.
- No feature flag; the refactor is self-contained and preserves the `getStageParams` contract, so `festival-orb-effects` tests remain green.
