## MODIFIED Requirements

### Requirement: Discovery bubble pool caching on re-entry
The system SHALL cache the last successfully generated bubble field (`Artist[]`) in a single app-lifetime store so that discovery page re-entries can paint real artists immediately without waiting on network RPCs. There SHALL be exactly one authoritative bubble-field cache; the raw `listTop` SWR cache and the display-field cache SHALL NOT be maintained as two independent snapshots of the same field.

#### Scenario: Re-entry paints cached artists instantly
- **WHEN** the user navigates to Discovery after a prior visit
- **AND** at least one cached artist is not yet followed
- **THEN** the bubble field SHALL be initialized from the cached field synchronously while the page loads
- **AND** followed artists SHALL be excluded as part of producing the field
- **AND** no ghost bubbles SHALL be shown
- **AND** any background refresh SHALL reconcile the field via a non-destructive delta (see "Re-entry preserves the in-session bubble field"), NOT a wholesale replacement that recomposes or shrinks the visible field

#### Scenario: Re-entry with all cached artists already followed
- **WHEN** the user navigates to Discovery after a prior visit
- **AND** every artist in the cached field has since been followed
- **THEN** producing the field SHALL exclude all of them, leaving the field empty (no stale bubbles rendered)
- **AND** the background refresh SHALL run immediately and refill the field with fresh artists
- **AND** the field SHALL remain empty until the refresh completes (ghost placeholder bubbles are NOT shown on the cached-but-filtered path, unlike a cold visit)

#### Scenario: Cache excludes followed artists on re-entry
- **WHEN** the cached bubble field contains artists that the user has since followed
- **THEN** those artists SHALL be excluded when the field is produced
- **AND** the followed artists SHALL NOT appear as bubbles in the physics engine

#### Scenario: Cold visit uses ghost bubbles
- **WHEN** Discovery is shown for the first time in the page and no field has been built yet (the initial load is still running)
- **THEN** the route SHALL initialize with ghost placeholder bubbles
- **AND** ghost bubbles SHALL switch to real artists in place as artists arrive (per seed on the similar-seed path, all at once on the top-artists path)

#### Scenario: Initial load starts during start-up when the app opens on Discovery
- **WHEN** the page is opened on Discovery
- **THEN** the initial load SHALL start during app start-up, without waiting for the route to load: once the session is known; for a signed-in fan, at once when follows are kept on the device for the account (see "Seeds come from the follows kept on the device"), otherwise after the follow list; and after restoring an onboarding guest's persisted follows
- **AND** if the field is built before the route shows it, the route SHALL show those artists directly, without ghost placeholder bubbles
- **AND** the route SHALL NOT start a second initial load while the start-up load is running

#### Scenario: Seeds come from the follows kept on the device
- **WHEN** a signed-in fan's follow list has been loaded on this device before, for the same account
- **AND** the app opens on Discovery
- **THEN** the start-up initial load SHALL choose its seeds from the followed artists kept from that load, without waiting for this session's follow list
- **AND** the field SHALL still exclude the artists in the follow list current when the field is set
- **AND** signing out SHALL remove the kept follows, and another account SHALL NOT use them

#### Scenario: Cache is updated after each successful load
- **WHEN** an initial load or refresh completes successfully
- **THEN** the resulting field SHALL be persisted to the single bubble-field cache
- **AND** the next re-entry SHALL use the updated field
