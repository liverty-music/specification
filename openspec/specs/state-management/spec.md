# State Management Specification

## Purpose

Defines the singleton service state owners (Onboarding, Guest) and how their state is persisted to and hydrated from localStorage.

## Requirements

### Requirement: FollowServiceClient as follow state SSoT

The `FollowServiceClient` singleton SHALL own `followedArtists: Artist[]` as `@observable` state, serving as the single source of truth for followed artists across all pages. It SHALL expose `followedIds` (derived `ReadonlySet<string>`) and `followedCount` (derived `number`) getters. For guest users, mutations delegate to `GuestService` for localStorage persistence. For authenticated users, mutations call the backend RPC.

#### Scenario: Hydrate from guest state

- **WHEN** `FollowServiceClient` is asked to hydrate during onboarding
- **THEN** it SHALL set `followedArtists` from `GuestService.follows` mapped to `Artist[]`
- **AND** Aurelia templates bound to `followService.followedCount` SHALL update automatically

#### Scenario: Follow an artist (guest)

- **WHEN** `follow(artist)` is called and the user is not authenticated
- **THEN** the system SHALL optimistically append the artist to `followedArtists`
- **AND** the system SHALL call `GuestService.follow(artist)` for localStorage persistence
- **AND** `followedIds` and `followedCount` SHALL reflect the new state immediately

#### Scenario: Follow an artist (authenticated)

- **WHEN** `follow(artist)` is called and the user is authenticated
- **THEN** the system SHALL optimistically append the artist to `followedArtists`
- **AND** the system SHALL call the backend Follow RPC
- **AND** on RPC failure, the system SHALL rollback `followedArtists` to its previous state

#### Scenario: Duplicate follow is no-op

- **WHEN** `follow(artist)` is called with an artist whose `id` is already in `followedIds`
- **THEN** `followedArtists` SHALL remain unchanged

#### Scenario: followedIds derivation

- **WHEN** `followedIds` is accessed
- **THEN** it SHALL return a `ReadonlySet<string>` derived from current `followedArtists` IDs

### Requirement: ConcertServiceClient concert search and tracking

The `ConcertServiceClient` singleton SHALL provide a `searchAndTrack(artistId, signal, targetCount, onConcertFound?)` method that encapsulates the full search lifecycle: initiate backend search, poll for completion, verify concerts on completion, and accumulate results in `artistsWithConcerts`. The service SHALL own `@observable artistsWithConcerts: Set<string>` tracking which artists have confirmed concerts.

#### Scenario: searchAndTrack initiates backend search

- **WHEN** `searchAndTrack(artistId)` is called
- **AND** the artist is not already tracked
- **THEN** the system SHALL call `searchNewConcerts(artistId)` fire-and-forget
- **AND** the system SHALL start polling via `setInterval` (2000ms) if not already running

#### Scenario: searchAndTrack for already-tracked artist is no-op

- **WHEN** `searchAndTrack(artistId)` is called for an artist already in the tracking map
- **THEN** the system SHALL NOT initiate a new search or duplicate the tracking entry

#### Scenario: Poll detects search completion

- **WHEN** `listSearchStatuses` returns `completed` for an artist
- **THEN** the system SHALL call `listConcerts(artistId)`
- **AND** if concerts exist, the system SHALL add `artistId` to `artistsWithConcerts`
- **AND** if an `onConcertFound` callback was provided, the system SHALL invoke it with the artist ID

#### Scenario: Poll detects search failure

- **WHEN** `listSearchStatuses` returns `failed` for an artist
- **THEN** the system SHALL mark the artist as done without checking concerts

#### Scenario: Per-artist timeout

- **WHEN** an artist's search has been pending for >= 15 seconds
- **THEN** the system SHALL mark the artist as done (timeout)

#### Scenario: Early polling stop at target

- **WHEN** `artistsWithConcerts.size` reaches the provided target count
- **THEN** the system SHALL stop polling immediately via `clearInterval`

#### Scenario: All searches complete stops polling

- **WHEN** all tracked artists have status `done`
- **AND** `artistsWithConcerts.size` has not yet reached the target
- **THEN** the system SHALL stop polling

#### Scenario: AbortSignal cancels polling

- **WHEN** the provided `AbortSignal` is aborted (e.g., page navigation)
- **THEN** the system SHALL stop polling via `clearInterval`
- **AND** the system SHALL retain `artistsWithConcerts` state (not clear it)

#### Scenario: artistsWithConcertsCount getter

- **WHEN** `artistsWithConcertsCount` is accessed
- **THEN** it SHALL return `artistsWithConcerts.size`
