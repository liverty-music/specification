## MODIFIED Requirements

### Requirement: Passion Level Tiers

The system SHALL support four hype level tiers for each followed artist, with emotion-based UI labels:

| Tier | Proto Value | Emoji | UI Label (ja) | UI Label (en) | Notification Scope |
|------|-------------|-------|----------------|----------------|-------------------|
| Watch | HYPE_TYPE_WATCH | 👀 | チェック | Watch | None |
| Home | HYPE_TYPE_HOME | 🔥 | 地元 | Home | Home area only |
| Nearby | HYPE_TYPE_NEARBY | 🔥🔥 | 近くも | Nearby | Within 200km |
| Away | HYPE_TYPE_AWAY | 🔥🔥🔥 | どこでも！ | Away | All concerts |

All four tiers SHALL be selectable by authenticated users via the SetHype RPC. No tier SHALL be rejected by server-side validation.

#### Scenario: Default hype level on follow

- **WHEN** a user follows a new artist
- **AND** the follow relationship is created
- **THEN** the hype level SHALL default to Watch (HYPE_TYPE_WATCH)

#### Scenario: UI labels use locale-appropriate phrasing

- **WHEN** hype level labels are displayed in the UI (slider header, dialogs, settings)
- **AND** the locale is Japanese
- **THEN** the system SHALL use emotion-based labels (チェック/地元/近くも/どこでも！)
- **WHEN** the locale is English
- **THEN** the system SHALL use proximity-based labels (Watch/Home/Nearby/Away)

#### Scenario: SetHype accepts all four tiers

- **WHEN** an authenticated user calls SetHype with any of the four defined hype tiers (WATCH, HOME, NEARBY, AWAY)
- **THEN** the system SHALL accept the request and persist the hype level
