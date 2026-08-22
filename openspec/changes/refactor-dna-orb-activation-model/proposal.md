## Why

On the Discovery screen the DNA orb's activation animation misfires: the orb reads as "activated" before/without a genuine follow, and the celebratory flash triggers on state changes that are not a user follow. This is a structural design flaw, not a one-off bug.

The orb conflates three distinct concerns into a single state observer (`followedCountChanged`): (A) the persistent stage level derived from follow count, (B) the one-shot gesture celebration (pulse/strobe/shockwave), and (C) bubble→orb color injection. Concern B's trigger (`pulse()`) is wired to the count-change observer, and concern A's applier (`setFollowCount()`) is called only from that same observer — never at initialization. Consequences:

- The celebratory flash fires on any follow-count change that is not a fresh gesture: guest-follow hydration on entry, guest→account migration, an unfollow, or an optimistic-update rollback.
- Aurelia 2 does not invoke a `@bindable` change handler for the value present at initial bind, so a returning user who enters Discovery already following N artists renders at stage 0 until the count next changes — the stage level is never seeded on entry.

The fix separates the two axes: stage level becomes a silent, idempotent function of the current count applied on entry and on every change; the celebration becomes an explicit one-shot fired only when a real follow absorption completes. This is frontend-only and was reviewed and approved for Aurelia 2 lifecycle correctness.

## What Changes

- The orb's **stage level** SHALL be applied idempotently and silently whenever the follow count is known — including on Discovery entry (first paint) and on any subsequent change from any source — with no celebratory side effect.
- The orb's **celebratory activation** (the one-shot flash) SHALL fire only when a genuine follow gesture's bubble absorption completes, unified on the same frame with the existing color injection, shockwave, and landing tone.
- Non-gesture follow-count changes (hydration, migration, unfollow, rollback) SHALL update the stage level silently and SHALL NOT trigger the celebratory flash.
- Stage-level transitions SHALL ease toward the new stage's targets rather than snapping, and a stage-level update SHALL NOT reset in-flight transient effects (e.g. particle trails).
- At zero follows with no follow performed this session, the orb SHALL present its unobtrusive baseline with no celebratory activation.
- The pure stage-parameter function (`getStageParams`, capability `festival-orb-effects`) is **unchanged**; its input→output contract at counts 0–5 is preserved.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `artist-discovery-dna-orb-ui`: Adds the requirement that the orb's celebratory activation is gesture-driven while the stage level tracks the follow count silently and idempotently (seeded on entry, eased transitions, no reset of transient effects). No change to the color-injection or burst requirements.

## Impact

- **Frontend only** (`liverty-music/frontend`). No proto, backend, or BSR changes.
- `src/components/dna-orb/dna-orb-canvas.ts` — `followedCountChanged` becomes a silent stage-level apply; the stage level is seeded after async size-init in `attached()`; the celebration is invoked only from `onAbsorbComplete()`.
- `src/components/dna-orb/orb-renderer.ts` — `setFollowCount` becomes an idempotent, side-effect-free stage-level apply that eases continuous quantities toward targets (via the existing `update(delta)` loop) and no longer wipes particle trails; `pulse()` becomes internal to a unified `celebrate()` entry point.
- `src/components/dna-orb/stage-effects.ts` — unchanged (pure, spec-pinned by `festival-orb-effects`).
- Existing dna-orb unit tests; add coverage for entry-seed, silent non-gesture updates, and gesture-only celebration.
