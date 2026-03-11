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

### Requirement: Hype Visual Indicators on Dashboard Cards

The system SHALL visually indicate hype (passion) levels on dashboard event cards using border gradient, glow effects, and neon text-shadow, without consuming additional card space.

#### Scenario: WATCH (Keep an Eye) card styling

- **WHEN** an event card is rendered for an artist with Keep an Eye hype level
- **THEN** the card SHALL have a `1px solid` border at `white/10` opacity
- **AND** the card SHALL NOT have glow or text-shadow effects
- **AND** no emoji badge SHALL be displayed

#### Scenario: HOME (Local Only) card styling

- **WHEN** an event card is rendered for an artist with Local Only hype level
- **THEN** the card SHALL have a `1px solid` border using the artist's color at 40% opacity
- **AND** the card SHALL have a subtle `box-shadow: 0 0 8px` glow using the artist's color at 30% opacity
- **AND** the artist name SHALL have a subtle `text-shadow: 0 0 4px` using the artist's color at 30% opacity
- **AND** no emoji badge SHALL be displayed

#### Scenario: NEARBY hype card styling

- **WHEN** an event card is rendered for an artist with Nearby hype level
- **THEN** the card SHALL have a `2px solid` border using the artist's color
- **AND** the card SHALL have a `box-shadow: 0 0 16px` glow using the artist's color at 50% opacity
- **AND** the artist name SHALL have a `text-shadow: 0 0 8px` neon effect using the artist's color at 60% opacity
- **AND** the glow SHALL animate with a gentle pulse (2-second cycle)
- **AND** no emoji badge SHALL be displayed

#### Scenario: AWAY (Must Go) card styling

- **WHEN** an event card is rendered for an artist with Must Go (Away) hype level
- **THEN** the card SHALL have a `2px` animated gradient border (conic-gradient rotation)
- **AND** the card SHALL have a layered glow: `box-shadow: 0 0 24px` at 60% opacity and `0 0 48px` at 20% opacity
- **AND** the artist name SHALL have a strong neon `text-shadow: 0 0 12px` and `0 0 24px` at 40% opacity
- **AND** the glow and gradient SHALL animate with a strong pulse (1.5-second cycle)
- **AND** no emoji badge SHALL be displayed

#### Scenario: Artist color source

- **WHEN** computing hype visual effects for an event card
- **THEN** the artist color SHALL be derived from the existing deterministic color generator (`color-generator.ts`)

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** all pulse and gradient rotation animations SHALL be disabled
- **AND** static border and glow styles SHALL remain visible
- **AND** text-shadow neon effects SHALL remain visible (they are static)

### Requirement: Emoji badge hype indicators on event cards (REMOVED)

**Reason**: Emoji badges overlap artist names in narrow lanes and consume card space. Replaced by zero-space border/glow/neon system.
**Migration**: Remove emoji badge elements from event card templates. Remove `HYPE_META` icon references from event card rendering. Hype visualization is now handled entirely via CSS classes based on hype level.
