## Architecture Design: Live Catalog API

## Context

The system needs to track artists and their concert schedules. This requires a stable data model for storing event details and an API for registering crawling targets.

## Goals / Non-Goals

- **Goals**: Define standard entities for Artist, Venue, and Concerts.
- **Non-Goals**: Implementation of the crawler logic itself (only the interface/schema).

## Decisions

### Decision: Entity Naming

- **Choice**: Use `Concert` instead of `Live`.
- **Reasoning**: `Concert` is the natural English term for music performances including rock/pop gigs and festivals. `Live` is Wasei-eigo (Japanese-English) when used as a noun and sounds unnatural to native speakers. `Event` is too generic.

### Decision: Media Entity

- **Choice**: Introduce `Media` entity to manage artist's online presence.
- **Reasoning**: Artists may have multiple information sources (Official Site, Twitter, Instagram). `Media` is a generic and user-friendly name compared to `CrawlTarget`, as this info might be displayed to users in the future.

### Decision: Entity Structures

- **Artist**:
  - `id` (UUID)
  - `name` (string)
  - `media` (repeated Media) - List of official channels.
- **Media**:
  - `id` (UUID)
  - `type` (Enum: WEB, TWITTER, INSTAGRAM)
  - `url` (string)
- **Venue**:
  - `id` (UUID)
  - `name` (string)
- **Concert**:
  - `id` (UUID)
  - `artist_id` (UUID)
  - `venue_id` (UUID)
  - `date` (ISO Date)
  - `start_time` (Time)
  - `open_time` (Time) - Often distinct from start time.
  - `title` (string) - Tour name or specific event title.

### Decision: RPC Methods

- **Service**: `ConcertService`
  - `ListConcerts(artist_id) -> { concerts: []Concert }`
  - `CreateArtist(params) -> { artist: Artist }`: Register artist.
  - `CreateArtistMedia(media) -> {  }`: Register artist with known media.
  - `DeleteArtistMedia(media_id) -> {  }`: Register artist with known media.
  - `ListArtists() -> { artists: []Artist }`: For management UI.

## Migrations

- N/A (New capability)
