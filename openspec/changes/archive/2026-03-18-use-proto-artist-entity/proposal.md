## Why

The frontend maps proto-generated `Artist` entities into partial DTOs (`ArtistBubble`, `GuestFollow`, `FollowedArtist`) at multiple points. Each mapping discards data — discovery drops fanart, guest state drops everything except `id`/`name`, and the dashboard re-extracts what it needs. This caused a concrete bug: `logoColorProfile` data is available from ArtistService RPCs during onboarding but is lost before reaching the dashboard, so logo-based card backgrounds never render during the onboarding flow.

## What Changes

- Replace `ArtistBubble`, `GuestFollow`, and `FollowedArtist` interfaces with the BSR-generated proto `Artist` entity throughout the frontend
- Guest state stores serialized proto `Artist` objects instead of `{ artistId, name }`
- Dashboard and discovery components consume proto `Artist` directly, eliminating intermediate mapping functions (`toBubble`, manual fanart extraction)
- Physics/layout properties (`x`, `y`, `radius`) remain in a presentation-only wrapper that composes with `Artist`, not replaces it

## Capabilities

### New Capabilities

### Modified Capabilities
- `frontend-entity-layer`: Artist data representation changes from custom interfaces to proto-generated entities across all frontend layers (state, services, components)

## Impact

- **Frontend services**: `artist-service-client.ts`, `follow-service-client.ts`, `dashboard-service.ts`, `concert-service.ts`
- **State management**: `state/` (actions, reducer, middleware persistence)
- **Entity types**: `entities/follow.ts`, `entities/concert.ts`
- **Components**: `dna-orb/`, `live-highway/`, `my-artists/`
- **Custom attributes**: `artist-color.ts` (profile binding source changes)
- **No backend or proto changes required** — this is purely a frontend refactoring
