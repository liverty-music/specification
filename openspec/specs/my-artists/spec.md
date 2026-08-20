# Capability: My Artists

## Purpose

Display and manage the user's followed artists, providing list and grid views with passion level controls.
## Requirements

### Requirement: Hype Change Persisted for Guest Users

The system SHALL persist hype changes made by guest users to localStorage without reverting them, and SHALL keep hype editing fully decoupled from onboarding state. Changing a hype level SHALL NOT advance, complete, or otherwise mutate onboarding state, and a repeated hype change (second tap onward) SHALL always apply.

#### Scenario: Guest user changes hype during onboarding

- **WHEN** a guest user changes a hype level while `OnboardingService.isOnboarding` is `true`
- **AND** the user is not authenticated
- **THEN** the system SHALL persist the hype value in `GuestService` under `liverty:guest:hypes`
- **AND** the system SHALL NOT revert the hype change in the UI
- **AND** the system SHALL NOT mutate onboarding state (no step advance, no completion)
- **AND** the signup-prompt-banner SHALL already have been visible (per the `Signup Banner on My Artists` requirement in the `signup-prompt-banner` capability); no additional banner-visibility mutation is required by this change handler

#### Scenario: Repeated hype change applies every time

- **WHEN** a guest user changes a hype level
- **AND** then changes a hype level a second (or subsequent) time on the same or another artist
- **THEN** every change SHALL apply and persist
- **AND** no change SHALL be reverted due to onboarding state

#### Scenario: Guest user changes hype after onboarding completion

- **WHEN** a guest user (onboarding completed) changes a hype level on the My Artists page
- **THEN** the system SHALL persist the hype value in `GuestService`
- **AND** the system SHALL NOT show a modal dialog
- **AND** the signup-prompt-banner SHALL remain visible (non-modal, persistent per its own capability spec)

### Requirement: View Toggle (List / Grid)

The My Artists page SHALL offer a view toggle between List view (default) and Grid (Festival) view.

#### Scenario: Toggling view mode

- **GIVEN** the My Artists page header
- **WHEN** the user taps the view toggle button
- **THEN** the page SHALL switch between List and Grid view

### Requirement: Grid (Festival) View

The Grid view SHALL display followed artists as poster-style tiles in a responsive grid layout.

#### Scenario: Away tiles are larger

- **GIVEN** the Grid view is active
- **WHEN** an artist has hype level Away (HYPE_TYPE_AWAY)
- **THEN** their tile SHALL span 2 columns and 2 rows

#### Scenario: Non-Away tiles are standard size

- **GIVEN** the Grid view is active
- **WHEN** an artist has hype level Watch, Home, or Nearby
- **THEN** their tile SHALL span 1 column and 1 row

#### Scenario: Long-press opens context menu

- **GIVEN** the Grid view is active
- **WHEN** the user long-presses a tile
- **THEN** a context menu SHALL appear with passion level options and an unfollow action

### Requirement: My Artists page help content documents all available gestures

The My Artists page help content SHALL explain how to unfollow an artist via the Edit-mode
toggle. The help text SHALL communicate that activating "Edit" in the page header reveals a
per-row remove control that unfollows immediately (with Undo). The help content SHALL NOT
reference a long-press-to-unfollow gesture (that interaction is retired). Desktop-specific
interactions need not be documented in help as they are visually self-evident.

#### Scenario: Help text visible to touch device users

- **WHEN** the user opens the My Artists page help (on any device, including touch)
- **THEN** help content includes an explanation that entering Edit mode reveals a per-row remove control to unfollow an artist
- **AND** the help content SHALL NOT mention a long-press unfollow gesture

#### Scenario: Help text available in all supported locales

- **WHEN** the app is displayed in any supported locale (Japanese, English)
- **THEN** the Edit-mode unfollow help text is translated and rendered correctly

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

