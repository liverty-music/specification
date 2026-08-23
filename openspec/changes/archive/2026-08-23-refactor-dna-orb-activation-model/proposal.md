## Why

On the Discovery screen the DNA orb's activation animation misfires: the orb reads as "activated" before/without a genuine follow, and the celebratory flash triggers on state changes that are not a user follow. This is a structural design flaw, not a one-off bug.

The orb conflates three distinct concerns into a single state observer (`followedCountChanged`): (A) the persistent stage level derived from follow count, (B) the one-shot gesture celebration (pulse/strobe/shockwave), and (C) bubble→orb color injection. Concern B's trigger (`pulse()`) is wired to the count-change observer, and concern A's applier (`setFollowCount()`) is called only from that same observer — never at initialization. Consequences:

- The celebratory flash fires on any follow-count change that is not a fresh gesture: guest-follow hydration on entry, guest→account migration, an unfollow, or an optimistic-update rollback.
- The orb reads as "activated" on Discovery entry: a returning user already following N artists sees the orb pre-rendered at the stage level for N (large radius, orbitals, light rays, glow) — activation before any genuine follow this session.

The fix makes the orb's activation **gesture-driven**: the orb enters dormant regardless of the user's total follow count, and both its stage growth and its celebration happen only when a genuine follow absorption completes. Its stage level tracks the follow gestures completed during the current session, not the total/historical count. This is frontend-only and was reviewed and approved for Aurelia 2 lifecycle correctness.

## What Changes

- The orb SHALL enter Discovery **dormant** (its unobtrusive baseline / level-0 look) regardless of the user's total follow count — it SHALL NOT be seeded to the stage for the historical count on entry.
- The orb's **stage level** SHALL be a function of the follow gestures completed during the current Discovery session (advancing one step per genuine follow absorption), NOT of the bound total follow count.
- The orb's **celebratory activation** (the one-shot flash) SHALL fire only when a genuine follow gesture's bubble absorption completes, unified on the same frame with the color injection, shockwave, and landing tone; the same absorption also advances the stage.
- Non-gesture follow-count changes (hydration, migration, unfollow, rollback) SHALL NOT move the orb or trigger the celebratory flash.
- Stage-level transitions SHALL ease toward the new stage's targets rather than snapping, and a stage-level update SHALL NOT reset in-flight transient effects (e.g. particle trails).
- With no follow performed this session, the orb SHALL present its unobtrusive baseline with no celebratory activation, regardless of total follow count.
- The pure stage-parameter function (`getStageParams`, capability `festival-orb-effects`) is **unchanged**; its input→output contract at counts 0–5 is preserved.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `artist-discovery-dna-orb-ui`: Adds the requirement that the orb's activation (both stage growth and celebration) is gesture-driven — the orb enters dormant regardless of the total follow count, advances one stage per genuine follow absorption (eased, no reset of transient effects), and never moves on non-gesture count changes. No change to the color-injection or burst requirements.

## Impact

- **Frontend only** (`liverty-music/frontend`). No proto, backend, or BSR changes.
- `src/components/dna-orb/dna-orb-canvas.ts` — the orb is seeded dormant (level 0) in `attached()`; a session-scoped `activationLevel` (not the bound total `followedCount`) drives the stage; `onAbsorbComplete()` is the sole path that advances the stage and fires the celebration; the total-count observer no longer moves the orb.
- `src/components/dna-orb/orb-renderer.ts` — `setFollowCount` becomes `applyLevel`, an idempotent, side-effect-free stage-level apply that eases continuous quantities toward targets (via the existing `update(delta)` loop) and no longer wipes particle trails; `pulse()` becomes internal to a unified `celebrate()` entry point.
- `src/components/dna-orb/stage-effects.ts` — unchanged (pure, spec-pinned by `festival-orb-effects`).
- Existing dna-orb unit tests; add coverage for dormant-on-entry, gesture-driven stage growth + celebration, no-op on non-gesture count changes, and idempotency.
