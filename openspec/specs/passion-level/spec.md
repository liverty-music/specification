# Capability: Passion Level

## Purpose

Allow users to express different levels of enthusiasm for followed artists, influencing how prominently their events appear on the Dashboard and whether push notifications are sent.

## Requirements

### Requirement: Passion Level Tiers

The system SHALL support three passion level tiers for each followed artist:

| Tier | Icon | Meaning |
|------|------|---------|
| Must Go | fire fire | User will travel anywhere for this artist |
| Local Only | fire | Default tier; events shown normally |
| Keep an Eye | eyes | Display on Dashboard but exclude from push notifications |

#### Scenario: Default passion level on follow

- **GIVEN** a user follows a new artist
- **WHEN** the follow relationship is created
- **THEN** the passion level SHALL default to Local Only

### Requirement: Passion Level Persistence

The system SHALL persist each user's passion level per followed artist in the backend database, enabling cross-device synchronization.

#### Scenario: Passion level survives session restart

- **GIVEN** a user sets an artist to Must Go
- **WHEN** the user closes and reopens the app
- **THEN** the artist SHALL still display as Must Go

### Requirement: SetPassionLevel API

The system SHALL provide a SetPassionLevel RPC endpoint that accepts an artist ID and a passion level, updating the user's preference for that artist.

#### Scenario: Successful update

- **GIVEN** an authenticated user who follows an artist
- **WHEN** the user calls SetPassionLevel with a valid artist ID and passion level
- **THEN** the system SHALL update the passion level and return success

#### Scenario: Unauthenticated request

- **GIVEN** an unauthenticated request
- **WHEN** the user calls SetPassionLevel
- **THEN** the system SHALL return an Unauthenticated error

#### Scenario: Invalid artist ID

- **GIVEN** an authenticated user
- **WHEN** the user calls SetPassionLevel without an artist ID
- **THEN** the system SHALL return an InvalidArgument error

### Requirement: PassionLevel in ListFollowed Response

The system SHALL include the user's passion level for each artist in the ListFollowed response, using a FollowedArtist wrapper that contains both the artist entity and the passion level.

#### Scenario: ListFollowed returns passion levels

- **GIVEN** a user follows three artists with different passion levels
- **WHEN** the user calls ListFollowed
- **THEN** each artist in the response SHALL include its corresponding passion level
