## ADDED Requirements

### Requirement: Orb Activation Separates Gesture Celebration From Follow-Count State

The system SHALL treat the DNA orb's celebratory activation (the one-shot flash/pulse and its associated strobe/staggered shockwaves) and its persistent stage level as two independent concerns. The celebratory activation SHALL fire ONLY when a genuine follow gesture's bubble absorption completes. The stage level (radius, orbital count, light rays, breathing, ground glow, and other quantities derived from the follow count) SHALL track the current follow count from any source — silently, idempotently, and including on first render — with no celebratory side effect. A stage-level update SHALL NOT reset in-flight transient effects.

The stage-parameter mapping itself (the pure `getStageParams(followCount)` function defined by `festival-orb-effects`) is unchanged by this requirement; this requirement governs WHEN and HOW that mapping is applied and WHEN the celebration fires, not the mapping's values.

#### Scenario: Stage level is seeded on Discovery entry

- **WHEN** the Discovery screen is entered
- **AND** the user already has N followed artists (e.g. restored/hydrated from a prior session before the canvas binds)
- **THEN** the orb SHALL render at the stage level for N on its first paint (radius, orbital count, light rays, ground glow, etc. consistent with `getStageParams(N)`)
- **AND** no celebratory activation flash SHALL fire

#### Scenario: Non-gesture follow-count changes update the stage silently

- **WHEN** the follow count changes for a reason other than a follow gesture completing on this screen — for example guest-follow hydration, guest→account migration on sign-in, an unfollow, or an optimistic-update rollback
- **THEN** the orb stage level SHALL update to match the new count
- **AND** no celebratory activation flash SHALL fire

#### Scenario: Celebration fires only on a real follow absorption

- **WHEN** a user follows an artist and the bubble absorption into the orb completes
- **THEN** the orb SHALL fire the celebratory activation together with the color injection, the shockwave (if enabled by the current stage level), and the landing tone on the same completion
- **AND** the follow-absorption completion SHALL be the only path that triggers the celebratory activation

#### Scenario: Unfollow does not celebrate

- **WHEN** the follow count decreases because the user unfollows an artist
- **THEN** the orb stage level SHALL step down to match the new count
- **AND** no celebratory activation flash SHALL fire

#### Scenario: Stage transitions are eased and preserve transient effects

- **WHEN** the stage level changes
- **THEN** the orb's continuous visual quantities (e.g. radius, base intensity) SHALL transition smoothly toward the new stage's targets rather than snapping instantaneously
- **AND** in-flight transient effects such as particle trails SHALL NOT be reset by the stage-level change

#### Scenario: Zero follows is dormant with no spurious activation

- **WHEN** the user has followed no artists (follow count is 0)
- **AND** the user has not completed a follow on this screen this session
- **THEN** the orb SHALL present its unobtrusive baseline (consistent with the "small seed radius / unobtrusive at zero follows" behavior)
- **AND** no celebratory activation flash SHALL fire
