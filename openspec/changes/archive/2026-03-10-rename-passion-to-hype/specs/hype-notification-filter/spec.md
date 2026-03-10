## ADDED Requirements

### Requirement: Hype-Based Notification Filtering

The system SHALL evaluate each follower's hype level and home area against a concert's venue location before sending a push notification. This filtering SHALL be applied within `NotifyNewConcerts()` after retrieving followers.

#### Scenario: WATCH follower receives no notification

- **WHEN** a new concert is discovered for an artist
- **AND** a follower has hype set to WATCH
- **THEN** the system SHALL skip push notification delivery for that follower

#### Scenario: HOME follower receives notification for home-area concert

- **WHEN** a new concert is discovered for an artist
- **AND** a follower has hype set to HOME
- **AND** the concert venue's adminArea matches the follower's home level_1 (ISO 3166-2)
- **THEN** the system SHALL send a push notification to that follower

#### Scenario: HOME follower does not receive notification for non-home concert

- **WHEN** a new concert is discovered for an artist
- **AND** a follower has hype set to HOME
- **AND** the concert venue's adminArea does NOT match the follower's home level_1
- **THEN** the system SHALL skip push notification delivery for that follower

#### Scenario: HOME follower with no home set receives no notification

- **WHEN** a new concert is discovered for an artist
- **AND** a follower has hype set to HOME
- **AND** the follower has not set a home area
- **THEN** the system SHALL skip push notification delivery for that follower

#### Scenario: ANYWHERE follower receives notification for all concerts

- **WHEN** a new concert is discovered for an artist
- **AND** a follower has hype set to ANYWHERE
- **THEN** the system SHALL send a push notification to that follower regardless of venue location

#### Scenario: NEARBY fallback in Phase 1

- **WHEN** a new concert is discovered for an artist
- **AND** a follower has hype set to NEARBY
- **THEN** the system SHALL treat the follower as ANYWHERE and send the notification

### Requirement: Followers With Hype Query

The system SHALL provide a repository method to retrieve followers of an artist along with their hype level and home area, enabling the notification filter to make decisions without additional queries.

#### Scenario: Retrieving followers with hype and home

- **WHEN** `NotifyNewConcerts()` needs to evaluate notification recipients
- **THEN** the system SHALL query followers joining `followed_artists`, `users`, and `homes` tables
- **AND** return each follower's user ID, hype level, and home level_1 (nullable)
