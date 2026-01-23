# Change: Define Live Catalog API

## Why

To collect and serve concert information, we need a formalized definition of the core domain entities (`Artist`, `Concert`, `Venue`) and the interfaces for managing them. This proposal establishes the schema and RPCs required for the "Live Information Collection" capability, enabling the crawler and frontend to communicate effectively.

## What Changes

- **New Capability**: `live-events`
- **New Entities**:
  - `Artist`: Represents a performer.
  - `Venue`: Represents a physical location for events.
  - `Concert`: Represents a specific music event (standard English naming over 'Live').
  - `Media`: Represents an artist's online presence (Web, Twitter, etc.).
- **New RPCs**:
  - `ConcertService`:
    - `ListConcerts`: Retrieve events for an artist.
    - `ListArtists`: List all registered artists.
    - `CreateArtist`: Register a new artist.
    - `CreateArtistMedia`: Add a media link to an artist.
    - `DeleteArtistMedia`: Remove a media link.

## Impact

- **Specs**: New `specs/live-events/spec.md`.
- **Backend**: Implementation of `ConcertService` and storage models.
- **Frontend**: Integration with `ConcertService` to display schedules.
