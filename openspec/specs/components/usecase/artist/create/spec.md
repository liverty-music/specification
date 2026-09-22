# Create

## Purpose

The `live-events` capability defines the core domain entities—Artists, Venues, and Concerts—and the standard interfaces for managing them. It establishes the single source of truth for concert metadata, enabling consistent data representation and access across the platform's crawler, backend services, and frontend applications.

## Requirements

### Requirement: Create an artist

The system MUST provide an interface to manage artists and their media links.

#### Scenario: Create Artist

- **WHEN** `CreateArtist` is called with a name
- **THEN** the system MUST create a new Artist entity and return it.

#### Scenario: List Artists

- **WHEN** `ListArtists` is called
- **THEN** the system MUST return a list of all registered artists.

#### Scenario: Add Media

- **WHEN** `CreateArtistMedia` is called with an artist ID, media type, and URL
- **THEN** the system MUST associate the media with the artist.

#### Scenario: Remove Media

- **WHEN** `DeleteArtistMedia` is called with a media ID
- **THEN** the system MUST remove the media association.
