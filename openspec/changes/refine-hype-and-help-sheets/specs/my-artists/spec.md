## MODIFIED Requirements

### Requirement: Hype Change Persisted for Guest Users

The system SHALL persist hype changes made by guest users to localStorage without reverting them, regardless of onboarding step.

#### Scenario: Guest user changes hype during MY_ARTISTS onboarding step

- **WHEN** a user at Step `'my-artists'` changes a hype level
- **AND** the user is not authenticated
- **THEN** the system SHALL persist the hype value in `GuestService` under `liverty:guest:hypes`
- **AND** the system SHALL NOT revert the hype change in the UI
- **AND** the system SHALL advance `onboardingStep` to `'completed'`
- **AND** the signup-prompt-banner SHALL already have been visible (per the `Signup Banner on My Artists` requirement in the `signup-prompt-banner` capability); no additional banner-visibility mutation is required by this change handler

#### Scenario: Guest user changes hype after onboarding completion

- **WHEN** a guest user (onboarding completed) changes a hype level on the My Artists page
- **THEN** the system SHALL persist the hype value in `GuestService`
- **AND** the system SHALL NOT show a modal dialog
- **AND** the signup-prompt-banner SHALL remain visible (non-modal, persistent per its own capability spec)

## ADDED Requirements

### Requirement: Default hype tier for new follows is Nearby

The system SHALL initialize every newly-created follow record with hype value `nearby` (proto enum `HYPE_TYPE_NEARBY`), regardless of whether the follow is created by a guest user (localStorage-backed) or an authenticated user (RPC-backed). The frontend constant `DEFAULT_HYPE` in `frontend/src/entities/follow.ts` SHALL be set to `'nearby'`.

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

### Requirement: My Artists hype column headers render invariant English

The artists-table column-header cells (`.hype-col-header` in `my-artists-route.html`) SHALL render the four hype tier labels as invariant English brand expressions (`Watch`, `Home`, `Nearby`, `Away`) directly in the template, not through an `entity.hype.values.*` i18n binding.

#### Scenario: Column header label rendering

- **WHEN** the My Artists table renders in either JA or EN locale
- **THEN** each `.hype-col-header` cell SHALL display `[emoji]` followed by the invariant English tier label
- **AND** the cell SHALL NOT contain a `<small t="entity.hype.values.*">` element

#### Scenario: Tier label per column

- **WHEN** the table renders
- **THEN** the four `.hype-col-header` cells SHALL display, in order:
  - `👀 Watch`
  - `🔥 Home`
  - `🔥🔥 Nearby`
  - `🔥🔥🔥 Away`
- **AND** these surface forms SHALL remain identical across all supported locales
