# Spec Delta

## MODIFIED Requirements

### Requirement: Fanart Data Propagation
The frontend service layer SHALL extract fanart image URLs from the `Artist.fanart` proto field in `FollowService.List` responses and propagate them to the `LiveEvent` and `FollowedArtist` view models for consumption by UI components.

#### Scenario: ListFollowed returns artist with fanart
- **WHEN** the `FollowService.List` RPC returns an artist with populated fanart data
- **THEN** the service layer SHALL map `hd_music_logo`, `music_logo`, `artist_background`, and `artist_thumb` URLs to the corresponding view model fields

#### Scenario: ListFollowed returns artist without fanart
- **WHEN** the `FollowService.List` RPC returns an artist without fanart data
- **THEN** the view model image URL fields SHALL be undefined or empty, triggering fallback display in UI components

#### Scenario: Dashboard events enriched with fanart
- **WHEN** the dashboard constructs `LiveEvent` objects from concert data
- **THEN** the system SHALL look up fanart URLs by artist ID from the `FollowService.List` response and attach them to the `LiveEvent`
