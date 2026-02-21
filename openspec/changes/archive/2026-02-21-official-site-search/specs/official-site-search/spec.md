## ADDED Requirements

### Requirement: Resolve Official Site URL from MusicBrainz

The system SHALL provide an `OfficialSiteResolver` interface that resolves an artist's official site URL from their MBID using the MusicBrainz url-rels API.

#### Scenario: Artist has an active official homepage relation

- **WHEN** `ResolveOfficialSiteURL` is called with a valid MBID
- **AND** MusicBrainz returns one or more `official homepage` relations with `ended = false`
- **THEN** the system SHALL return the URL whose `source-credit` matches the artist's current name (case-insensitive) as the first priority
- **AND** fall back to an unattributed (`source-credit = ""`) active URL as the second priority
- **AND** fall back to the first active URL if no name match is found

#### Scenario: All official homepage relations are ended

- **WHEN** `ResolveOfficialSiteURL` is called with a valid MBID
- **AND** all `official homepage` relations have `ended = true`
- **THEN** the system SHALL return an empty string without error

#### Scenario: No official homepage relation exists

- **WHEN** `ResolveOfficialSiteURL` is called with a valid MBID
- **AND** MusicBrainz returns no relation with `type = "official homepage"`
- **THEN** the system SHALL return an empty string without error

#### Scenario: MusicBrainz API is unavailable

- **WHEN** `ResolveOfficialSiteURL` is called and the MusicBrainz API returns an error
- **THEN** the system SHALL return the error to the caller

### Requirement: Async Official Site Persistence on Follow

The system SHALL asynchronously resolve and persist the official site URL for an artist immediately after a user follow is recorded.

#### Scenario: Official site is successfully resolved and persisted

- **WHEN** a user successfully follows an artist that has no existing `artist_official_site` record
- **AND** MusicBrainz returns a non-empty URL for the artist's MBID
- **THEN** the system SHALL create an `artist_official_site` record with the resolved URL
- **AND** the Follow RPC SHALL return success without waiting for resolution to complete

#### Scenario: Official site already exists

- **WHEN** a user follows an artist that already has an `artist_official_site` record
- **THEN** the system SHALL skip resolution and creation silently

#### Scenario: MusicBrainz returns no URL

- **WHEN** resolution returns an empty string
- **THEN** the system SHALL not create an `artist_official_site` record
- **AND** SHALL NOT return an error to the Follow caller

#### Scenario: Resolution fails with an error

- **WHEN** the MusicBrainz API returns an error during async resolution
- **THEN** the error SHALL be logged at WARN level
- **AND** SHALL NOT affect the Follow RPC response
