## MODIFIED Requirements

### Requirement: Passion Level Tiers

The system SHALL support four hype level tiers for each followed artist, with emotion-based UI labels:

| Tier | Proto Value | Emoji | UI Label (ja) | UI Label (en) | Notification Scope |
|------|-------------|-------|----------------|----------------|-------------------|
| Watch | HYPE_TYPE_WATCH | 👀 | チェック | Just checking | None |
| Home | HYPE_TYPE_HOME | 🔥 | 地元 | Local shows | Home area only |
| Nearby | HYPE_TYPE_NEARBY | 🔥🔥 | 近くも | Nearby too | Within 200km (Phase 2) |
| Away | HYPE_TYPE_AWAY | 🔥🔥🔥 | どこでも！ | Anywhere! | All concerts |

#### Scenario: Default hype level on follow

- **WHEN** a user follows a new artist
- **AND** the follow relationship is created
- **THEN** the hype level SHALL default to Watch (HYPE_TYPE_WATCH)

#### Scenario: UI labels use emotion-based phrasing

- **WHEN** hype level labels are displayed in the UI (slider header, dialogs, settings)
- **THEN** the system SHALL use emotion-based labels (チェック/地元/近くも/どこでも！) instead of proximity-based labels (Watch/Home/NearBy/Away)

### Requirement: Hype Changes Require Authentication

The system SHALL prevent unauthenticated users from changing hype levels. Hype state SHALL NOT be persisted in localStorage.

#### Scenario: Unauthenticated user attempts hype change

- **WHEN** an unauthenticated user attempts to change a hype level (via slider tap or any UI control)
- **THEN** the system SHALL NOT update the hype level
- **AND** the system SHALL trigger a signup prompt flow
- **AND** no hype value SHALL be written to localStorage

#### Scenario: Authenticated user changes hype

- **WHEN** an authenticated user changes a hype level
- **THEN** the system SHALL call `SetHype` RPC and persist the change on the backend
- **AND** the UI SHALL update optimistically
