<!-- spec: my-artists | target: components/usecase/follow/follow | flags: CLASSNAME | new_name: Default hype tier for new follows is Nearby -->

### Requirement: Default hype tier for new follows is Nearby

The system SHALL initialize every newly-created follow record with hype value `nearby` (proto enum `HYPE_TYPE_NEARBY`), regardless of whether the follow is created by a guest user (localStorage-backed) or an authenticated user (RPC-backed). The frontend constant `DEFAULT_HYPE` SHALL be set to `'nearby'`.

#### Scenario: Guest follows an artist from Discovery

- **WHEN** a guest user taps an artist bubble on the Discovery page to follow them
- **THEN** the resulting follow record stored in `GuestService` SHALL have `hype: 'nearby'`
- **AND** the artist SHALL appear on the My Artists page with the Nearby dot (third position) visually active

#### Scenario: Authenticated user follows an artist

- **WHEN** an authenticated user follows an artist via the Discovery flow
- **THEN** the follow record stored by the backend (after `Follow` RPC succeeds) SHALL have `hype = HYPE_TYPE_NEARBY`
- **AND** subsequent `ListFollowed` responses SHALL return that artist with the Nearby hype value until the user explicitly changes it

#### Scenario: Guest-data merge respects new default

- **WHEN** a guest user with follows at the default `nearby` value completes signup
- **AND** the guest-data merge service processes those follows
- **THEN** the merge service SHALL still suppress merging follows that match the default value (`nearby`), so that an authenticated user's pre-existing hype setting for the same artist is not overwritten by a guest record that simply held the default

#### Scenario: Explicit guest "Nearby" choice indistinguishable from passive default acceptance (known limitation)

- **WHEN** a guest user deliberately sets a follow's hype to `nearby` (for example by following the artist, changing the tier to `away`, then changing back to `nearby`)
- **AND** the guest later signs up and the guest-data merge service runs
- **THEN** the merge service SHALL apply the same suppression as for passive default acceptance (no SetHype RPC call), because the persisted guest hype value `nearby` carries no marker distinguishing "explicit choice" from "default left untouched"
- **AND** if the authenticated user's backend record for that artist holds a different hype value (legacy `watch` from before the default flip, or a tier set on another device), the guest's explicit `nearby` choice SHALL NOT overwrite it
- **AND** this is an accepted limitation of the current suppression heuristic; resolving it would require either a separate "explicit-set" flag in guest storage or always calling SetHype during merge (which would overwrite legitimate non-default backend values). The trade-off is revisited only if the limitation becomes observably user-visible.

#### Scenario: Existing stored records are not migrated

- **WHEN** the `DEFAULT_HYPE` change ships
- **AND** a user has previously-stored follow records with `hype = 'watch'`
- **THEN** the stored values SHALL remain `'watch'`; only newly-created follows SHALL receive `'nearby'`
- **AND** no database migration or client-side mutation SHALL alter the existing records
