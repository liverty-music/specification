## MODIFIED Requirements

### Requirement: Passion Level Tiers

The system SHALL support four hype level tiers for each followed artist, with emotion-based UI labels:

| Tier | Proto Value | Emoji | UI Label (ja) | UI Label (en) | Notification Scope |
|------|-------------|-------|----------------|----------------|-------------------|
| Watch | HYPE_TYPE_WATCH | 👀 | チェック | Just checking | None |
| Home | HYPE_TYPE_HOME | 🔥 | 地元 | Local shows | Home area only |
| Nearby | HYPE_TYPE_NEARBY | 🔥🔥 | 近くも | Nearby too | Within 200km |
| Away | HYPE_TYPE_AWAY | 🔥🔥🔥 | どこでも！ | Anywhere! | All concerts |

All four tiers SHALL be selectable by authenticated users via the SetHype RPC. No tier SHALL be rejected by server-side validation.

#### Scenario: Default hype level on follow

- **WHEN** a user follows a new artist
- **AND** the follow relationship is created
- **THEN** the hype level SHALL default to Watch (HYPE_TYPE_WATCH)

#### Scenario: UI labels use emotion-based phrasing

- **WHEN** hype level labels are displayed in the UI (slider header, dialogs, settings)
- **THEN** the system SHALL use emotion-based labels (チェック/地元/近くも/どこでも！) instead of proximity-based labels (Watch/Home/NearBy/Away)

#### Scenario: SetHype accepts all four tiers

- **WHEN** an authenticated user calls SetHype with any of the four defined hype tiers (WATCH, HOME, NEARBY, AWAY)
- **THEN** the system SHALL accept the request and persist the hype level

### Requirement: SetHype API

The system SHALL provide a SetHype RPC endpoint that accepts an artist ID and a hype level, updating the user's preference for that artist. The endpoint SHALL accept all four defined HypeType values (WATCH, HOME, NEARBY, AWAY).

#### Scenario: Successful update

- **GIVEN** an authenticated user who follows an artist
- **WHEN** the user calls SetHype with a valid artist ID and hype level
- **THEN** the system SHALL update the hype level and return success

#### Scenario: Unauthenticated request

- **GIVEN** an unauthenticated request
- **WHEN** the user calls SetHype
- **THEN** the system SHALL return an Unauthenticated error

#### Scenario: Invalid artist ID

- **GIVEN** an authenticated user
- **WHEN** the user calls SetHype without an artist ID
- **THEN** the system SHALL return an InvalidArgument error

