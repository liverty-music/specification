## MODIFIED Requirements

### Requirement: Passion Level Tiers

The system SHALL support four hype tiers for each followed artist:

| Tier | Value | Meaning |
|------|-------|---------|
| Watch | `watch` | Dashboard view only, no push notifications |
| Home | `home` | Push notifications for home area concerts only |
| Nearby | `nearby` | Reserved for Phase 2 (physical proximity); not user-selectable |
| Away | `away` | Push notifications for all concerts nationwide (default on follow) |

The term "passion level" is renamed to "hype" throughout code, proto, and specs.

#### Scenario: Default hype on follow

- **GIVEN** a user follows a new artist
- **WHEN** the follow relationship is created
- **THEN** the hype SHALL default to Away
