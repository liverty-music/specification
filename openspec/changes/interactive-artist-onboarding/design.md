## Context

Currently, the `ConcertService` handles both "artist information management" and "concert information management," which should be separated. Additionally, there is no feature for users to follow (favorite) artists, meaning there is no starting point for a personalized experience.
To provide a chain-like discovery experience utilizing the Last.fm API, we will perform service separation and implement new UX.

## Goals / Non-Goals

**Goals:**
- Established the `ArtistService` and transferred responsibilities from `ConcertService`.
- Retrieved "popular artists" and "similar artists" using the Last.fm API.
- Implemented an artist follow feature for users.
- Implemented an onboarding UI that integrates search, follow, and chain-like discovery (drill-down).

**Non-Goals:**
- Automated search for live information for followed artists (this will be a separate task running `SearchNewConcerts` asynchronously).
- Implementation of YouTube history analysis logic (out of scope for this specific change).

## Decisions

### 1. Service Separation (Refactoring)
**Decision**: Move and consolidate all RPCs related to artist CRUD, metadata, and follow status into `ArtistService`.
**Rationale**: Clarification of responsibilities. To facilitate future functional extensions such as "artist detail pages" and "recommended artists."

### 2. Follow (Watch) Data Model
**Decision**: Create a new `followed_artists` table to manage `user_id` and `artist_id` pairs.
**Rationale**: While following festivals or venues may be considered in the future, we will first focus specifically on individual artists.

### 3. Last.fm API Proxy
**Decision**: Do not access Last.fm directly from the frontend; access via the backend's `ArtistService` (`ListSimilar`, `ListTop`).
**Rationale**:
- Secrecy of API keys.
- To check artists included in the results against the DB and assign IDs as necessary.
- Control of rate limits, etc.

**Endpoints Used**:
- **Search (Incremental Search)**:
  - Method: `artist.search`
  - URL: `http://ws.audioscrobbler.com/2.0/?method=artist.search&artist={artist_name}&api_key={api_key}&format=json`
- **Similar Artists (Chain-like Follow Feature)**:
  - Method: `artist.getSimilar`
  - URL: `http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist={artist_name}&api_key={api_key}&format=json`
- **Top Artists (Initial Display - Popular Artists in Japan)**:
  - Method: `geo.getTopArtists`
  - URL: `http://ws.audioscrobbler.com/2.0/?method=geo.gettopartists&country=japan&api_key={api_key}&format=json`

### 4. UI Transition Management
**Decision**:
- `ListTop`: "Popular artists in Japan" that the user first sees.
- `Search`: Incremental search.
- `Follow`: Call `ListSimilar` after execution using that artist as a seed to transition to "chain suggestion mode."
- `Reset`: Clear all filters and return to the `ListTop` results.

## Risks / Trade-offs

- **[Risk] Inaccurate Data from Last.fm** → Duplicate data may occur on the DB as deduplication is performed only by artist name.
  - **Mitigation**: Perform simple normalization by artist name upon retrieval; if it exists in the DB, use that ID; otherwise, treat it as a candidate for new creation.
- **[Trade-off] Performance of Incremental Search** → Delays occur if the external API is called every time.
  - **Mitigation**: Perform caching on the backend or initially perform search only on the DB.
