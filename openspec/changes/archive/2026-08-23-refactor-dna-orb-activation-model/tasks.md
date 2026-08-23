## 1. Renderer: silent, idempotent stage level (orb-renderer.ts)

- [x] 1.1 Rename `setFollowCount(count)` → `applyLevel(count)`; recompute `stageParams = getStageParams(count)` and set **target** values for `baseIntensity` and `orbRadius` (do not snap).
- [x] 1.2 Remove the particle-trail wipe from the level apply (it is transient state, unrelated to stage level; required for idempotency).
- [x] 1.3 In `update(delta)`, ease current `baseIntensity`/`orbRadius` toward their targets (mirror the existing `pulseIntensity`/`swirlIntensity` decay pattern). No per-call timers/rAF.
- [x] 1.4 Make `pulse()` private; add a private `celebrate(hue)` that unifies `pulse()` + `injectColor(hue)` + gated `spawnShockwave(hue)` + landing tone on one frame. (Keep `injectColor`/`spawnShockwave` callable as today; `celebrate` composes them.)

## 2. Canvas: gesture-driven activation (dna-orb-canvas.ts)

- [x] 2.1 Drive the orb from a session-scoped `activationLevel` (0 on entry, reset per component mount), NOT the bound total `followedCount`. Remove the `followedCountChanged` observer so non-gesture total-count changes (hydration/migration/unfollow/rollback) never move the orb. `applyLevel(level)` still folds in `updateOrbZone`/`cometTrailEnabled`.
- [x] 2.2 Seed the orb DORMANT in `attached()`: after `await this.initWhenSized()` and the `if (this.detached) return` guard, before `physics.addBubbles(...)`, call `this.applyLevel(this.activationLevel)` (level 0) — the orb enters at its baseline regardless of the user's total follow count.
- [x] 2.3 In `onAbsorbComplete(hue)` (the sole genuine-follow-landing path), increment `activationLevel`, `applyLevel(this.activationLevel)` to advance one eased stage, then fire the unified `celebrate(hue)` + landing tone. This is the only path that advances the stage or celebrates; the shockwave gate reads the same `stageParams` `applyLevel` set.

## 3. Tests

- [x] 3.1 Dormant-on-entry: mounting the canvas with `followedCount = N` (N>0) seeds the orb at level 0 (assert `applyLevel(0)`, not N), with no pulse.
- [x] 3.2 Gesture-driven growth: each `onAbsorbComplete` advances `activationLevel` (applyLevel 1, then 2, …), celebrates once, and plays the tone; non-gesture total-count changes do not move the orb (observer removed).
- [x] 3.3 Gesture celebration: `celebrate(hue)` unifies pulse + color inject + shockwave (when enabled) + tone, fired only from `onAbsorbComplete`.
- [x] 3.4 Idempotency: repeated `applyLevel(n)` does not reset in-flight particle trails.
- [x] 3.5 Confirm `festival-orb-effects` `getStageParams` tests remain unchanged and green (no edits to `stage-effects.ts`).

## 4. Verify & ship

- [x] 4.1 `make check` (lint + typecheck + unit) passes in `frontend`.
- [x] 4.2 Verify on Discovery (live prod UI via the Aurelia VM at v1.58.3): entry with N>0 follows → orb dormant (level 0, no flash); a genuine follow → one-stage activation + celebration; non-gesture count changes do not move the orb.
- [x] 4.3 Open the frontend PR, merge after CI + review.
- [x] 4.4 Ship to production via the frontend release path and confirm the orb behavior in the prod environment.
