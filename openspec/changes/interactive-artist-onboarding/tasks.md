## 1. Domain Entities & Database

- [x] 1.1 Create `followed_artists` table (migration)
- [x] 1.2 Update `entity.Artist` to include common fields for different providers
- [x] 1.3 Implementation of `ArtistRepository` with follow/unfollow support

## 2. Service Refactoring (`ArtistService`)

- [x] 2.1 Implementation of `ArtistService` handler in `internal/adapter/rpc`
- [x] 2.2 Relocation of artist-related methods from `ConcertService`
- [x] 2.3 Dependency injection updates in the main stack

## 3. External API Integration

- [x] 3.1 Last.fm API client implementation details (Throttler integration)
- [x] 3.2 Result normalization: Mapping Last.fm results to internal `Artist` entity
- [x] 3.3 Caching strategy for search and similar results

## 4. Onboarding UI (Aurelia 2)

- [x] 4.1 Component for "Popular Artists" (initial view)
- [x] 4.2 Incremental search with debounce logic
- [x] 4.3 Chain-follow interaction and state management
- [x] 4.4 Visual feedback for follow/unfollow actions
