## 1. Renderer: silent, idempotent stage level (orb-renderer.ts)

- [ ] 1.1 Rename `setFollowCount(count)` → `applyLevel(count)`; recompute `stageParams = getStageParams(count)` and set **target** values for `baseIntensity` and `orbRadius` (do not snap).
- [ ] 1.2 Remove the particle-trail wipe from the level apply (it is transient state, unrelated to stage level; required for idempotency).
- [ ] 1.3 In `update(delta)`, ease current `baseIntensity`/`orbRadius` toward their targets (mirror the existing `pulseIntensity`/`swirlIntensity` decay pattern). No per-call timers/rAF.
- [ ] 1.4 Make `pulse()` private; add a private `celebrate(hue)` that unifies `pulse()` + `injectColor(hue)` + gated `spawnShockwave(hue)` + landing tone on one frame. (Keep `injectColor`/`spawnShockwave` callable as today; `celebrate` composes them.)

## 2. Canvas: split state-apply from gesture-celebration (dna-orb-canvas.ts)

- [ ] 2.1 `followedCountChanged(newVal)` → body becomes `applyLevel(newVal)` only; fold the current `updateOrbZone`/`cometTrailEnabled` calls into `applyLevel` so both the seed and the mutation path get them. Remove the `pulse()` call.
- [ ] 2.2 Seed the stage in `attached()`: after `await this.initWhenSized()` and the `if (this.detached) return` guard, before `physics.addBubbles(...)`, call `this.applyLevel(this.followedCount)` (reads the freshest count post-await).
- [ ] 2.3 In `onAbsorbComplete(hue)`, call the unified `celebrate(hue)` (the sole celebration trigger). Ensure the stage gate for the shockwave reads the same `stageParams` the seed/apply set.

## 3. Tests

- [ ] 3.1 Entry-seed: mounting the canvas with `followedCount = N` (N>0) renders at stage N on first paint (assert `orbRadius`/stage params reflect N), with no pulse.
- [ ] 3.2 Silent non-gesture update: driving `followedCountChanged` (hydrate/migrate/unfollow/rollback simulation) updates the stage level but does NOT invoke the celebration.
- [ ] 3.3 Gesture celebration: completing an absorption (`onAbsorbComplete`) invokes `celebrate` exactly once and unifies pulse + color inject + shockwave (when enabled) + tone.
- [ ] 3.4 Idempotency: repeated `applyLevel(n)` does not reset in-flight particle trails.
- [ ] 3.5 Confirm `festival-orb-effects` `getStageParams` tests remain unchanged and green (no edits to `stage-effects.ts`).

## 4. Verify & ship

- [ ] 4.1 `make check` (lint + typecheck + unit) passes in `frontend`.
- [ ] 4.2 Manually verify on Discovery: fresh 0-follow entry → dormant orb, no flash; first follow → single unified celebration on absorption; re-enter with existing follows → correct stage on first paint, no flash; unfollow → eases down silently.
- [ ] 4.3 Open the frontend PR, merge after CI + review.
- [ ] 4.4 Ship to production via the frontend release path and confirm the orb behavior in the dev/prod environment.
