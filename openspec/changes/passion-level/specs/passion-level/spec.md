# Passion Level

## Purpose

Enables users to express different levels of enthusiasm for followed artists, affecting how events are displayed on the Dashboard and whether push notifications are sent. This creates a personalized priority system where "must-go" artists get visually prominent treatment across all geographical lanes.

## Requirements

### Requirement: Passion Level Tiers
The system SHALL support three passion level tiers for each followed artist.

#### Scenario: Must Go level
- **WHEN** a user sets an artist's passion level to Must Go (🔥🔥)
- **THEN** the system SHALL treat that artist's events as high priority across all Dashboard lanes
- **AND** events in Lane 2 and Lane 3 SHALL render with Visual Mutation UI (expanded, accented)
- **AND** the artist SHALL be eligible for push notifications regardless of event location

#### Scenario: Local Only level (default)
- **WHEN** a user follows an artist without changing the passion level
- **THEN** the passion level SHALL default to Local Only (🔥)
- **AND** events SHALL render normally according to standard lane rules
- **AND** the artist SHALL be eligible for push notifications for local events only

#### Scenario: Keep an Eye level
- **WHEN** a user sets an artist's passion level to Keep an Eye (👀)
- **THEN** events SHALL render normally on the Dashboard
- **AND** the artist SHALL NOT be included in push notifications

---

### Requirement: Backend Persistence
The system SHALL persist passion level as part of the artist-following relationship.

#### Scenario: Setting passion level via API
- **WHEN** a `SetPassionLevel` RPC is called with a valid artist ID and passion level
- **THEN** the system SHALL update the `passion_level` column in the `followed_artists` table
- **AND** the response SHALL confirm the update

#### Scenario: Setting passion level for unfollowed artist
- **WHEN** a `SetPassionLevel` RPC is called for an artist the user does not follow
- **THEN** the system SHALL return a NOT_FOUND error

#### Scenario: Retrieving passion level
- **WHEN** `ListFollowed` is called
- **THEN** each followed artist in the response SHALL include their current passion level
