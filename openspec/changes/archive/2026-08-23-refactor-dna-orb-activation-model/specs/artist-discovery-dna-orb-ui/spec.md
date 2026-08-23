## ADDED Requirements

### Requirement: Orb Activation Separates Gesture Celebration From Follow-Count State

The DNA orb's activation SHALL be gesture-driven: the orb SHALL enter Discovery dormant (its unobtrusive baseline) and SHALL advance its stage level and fire its celebration ONLY in response to a genuine follow gesture's bubble absorption completing on this screen. The orb's stage level SHALL be a function of the follow gestures completed during the current Discovery session — NOT of the user's total/historical follow count — so the orb never reads as "activated" before a genuine follow, regardless of how many artists the user already follows. Non-gesture follow-count changes (guest-follow hydration, guest→account migration, unfollow, optimistic-update rollback) SHALL NOT move the orb or fire the celebration. A stage-level update SHALL NOT reset in-flight transient effects.

The stage-parameter mapping itself (the pure `getStageParams(level)` function defined by `festival-orb-effects`) is unchanged by this requirement; this requirement governs WHEN and HOW that mapping is applied and WHEN the celebration fires, not the mapping's values.

#### Scenario: Orb enters dormant regardless of total follow count

- **WHEN** the Discovery screen is entered
- **AND** the user already has N followed artists (e.g. restored/hydrated from a prior session before the canvas binds)
- **THEN** the orb SHALL render at its dormant baseline on first paint (the level-0 look: small radius, no orbitals, no light rays), NOT at the stage level for N
- **AND** no celebratory activation flash SHALL fire

#### Scenario: Non-gesture follow-count changes do not move the orb

- **WHEN** the follow count changes for a reason other than a follow gesture completing on this screen — for example guest-follow hydration, guest→account migration on sign-in, an unfollow, or an optimistic-update rollback
- **THEN** the orb SHALL NOT change its stage level
- **AND** no celebratory activation flash SHALL fire

#### Scenario: A genuine follow both advances the stage and celebrates

- **WHEN** a user follows an artist and the bubble absorption into the orb completes
- **THEN** the orb SHALL advance its stage level by one step (session-scoped) toward the new stage's targets
- **AND** the orb SHALL fire the celebratory activation together with the color injection, the shockwave (if enabled by the current stage level), and the landing tone on the same completion
- **AND** the follow-absorption completion SHALL be the only path that advances the stage or triggers the celebratory activation

#### Scenario: Unfollow does not move the orb or celebrate

- **WHEN** the follow count decreases because the user unfollows an artist
- **THEN** the orb SHALL NOT change its stage level
- **AND** no celebratory activation flash SHALL fire

#### Scenario: Stage transitions are eased and preserve transient effects

- **WHEN** a genuine follow advances the stage level
- **THEN** the orb's continuous visual quantities (e.g. radius, base intensity) SHALL transition smoothly toward the new stage's targets rather than snapping instantaneously
- **AND** in-flight transient effects such as particle trails SHALL NOT be reset by the stage-level change

#### Scenario: Zero follows this session is dormant with no spurious activation

- **WHEN** the user has not completed a follow on this screen this session
- **THEN** the orb SHALL present its unobtrusive baseline (the level-0 "small seed radius / unobtrusive" look), regardless of the user's total follow count
- **AND** no celebratory activation flash SHALL fire
