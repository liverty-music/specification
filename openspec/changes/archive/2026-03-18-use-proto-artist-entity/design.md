## Context

The frontend currently defines three custom interfaces to represent artist data at different layers:

- **`ArtistBubble`** (discovery): `{ id, name, mbid, imageUrl, x, y, radius }` — used by Matter.js physics in dna-orb canvas
- **`GuestFollow`** (state): `{ artistId, name }` — persisted to localStorage during onboarding
- **`FollowedArtist`** (dashboard): `{ id, name, hype, logoUrl, backgroundUrl, logoColorProfile }` — manually extracted from proto response

Each mapping discards fields. ArtistService RPCs (ListTop, Search, ListSimilar) return full proto `Artist` entities with `Fanart` (including `LogoColorProfile`), but `toBubble()` strips everything except `id/name/mbid`. When the guest store saves a follow, only `artistId/name` survives. The dashboard then has no fanart data during onboarding.

**Affected files (19):**
- Services: `artist-service-client.ts`, `follow-service-client.ts`, `dashboard-service.ts`, `local-artist-client.ts`, `guest-data-merge-service.ts`
- State: `app-state.ts`, `middleware.ts`
- Entities: `follow.ts`, `concert.ts`
- Discovery: `discovery-route.ts`, `follow-orchestrator.ts`, `genre-filter-controller.ts`, `search-controller.ts`, `bubble-manager.ts`
- Components: `dna-orb-canvas.ts`, `bubble-physics.ts`, `my-artists-route.ts`
- Custom attributes: `artist-color.ts`

## Goals / Non-Goals

**Goals:**
- Use BSR-generated proto `Artist` as the single artist representation across all frontend layers
- Preserve `logoColorProfile` and fanart URLs from discovery through guest state to dashboard
- Eliminate `ArtistBubble`, `GuestFollow`, and `FollowedArtist` custom interfaces
- Persist proto `Artist` objects in localStorage during onboarding (via `toJson`/`fromJson`)

**Non-Goals:**
- Modifying backend or proto definitions — this is purely frontend
- Changing Matter.js physics logic — only the data wrapper changes
- Adding new RPC calls — existing RPCs already return the data we need

## Decisions

### Decision 1: Use proto `Artist` directly, compose with physics props

The BSR-generated `Artist` class (from `artist_pb.js`) becomes the canonical artist type. For discovery's Matter.js physics, use a composition type:

```typescript
interface PhysicsBubble {
  artist: Artist
  x: number
  y: number
  radius: number
}
```

**Why not extend Artist?** Proto classes are generated and sealed. Composition is the standard pattern for adding presentation-only concerns.

**Alternative considered:** Keep `ArtistBubble` but populate fanart fields → still creates a parallel type that drifts from proto, same class of bug will recur.

### Decision 2: Serialize proto Artist to localStorage via `toJsonString`/`fromJsonString`

Proto-ES classes support `toJsonString()` and `fromJson()`. Use these for localStorage persistence in the guest state middleware.

**Why not `JSON.stringify`?** Proto classes use specific field casing (`hdMusicLogo` not `hd_music_logo`) and `toJsonString()` handles this correctly. `fromJson()` reconstructs the full proto instance including nested messages.

**Trade-off:** localStorage payload increases from ~50 bytes/artist to ~500-2000 bytes/artist (with fanart). For 30 followed artists this is ~60KB — well within localStorage limits.

### Decision 3: Replace `FollowedArtist` with proto `Artist` + hype

The `FollowedArtist` interface exists because `ListFollowed` RPC returns `FollowedArtist` proto messages (artist + hype). Keep using this proto type directly:

```typescript
// Before: manual extraction
{ id: fa.artist?.id?.value ?? '', name: ..., logoUrl: fanart?.hdMusicLogo?.value ... }

// After: pass proto object through
{ artist: fa.artist, hype: fa.hype }
```

Components that need specific fields (e.g., `logoUrl`) extract them at the template or component level, not in the service layer.

### Decision 4: Dashboard artistMap keyed by proto `Artist`

The `DashboardService.artistMap` changes from `Map<string, FollowedArtist>` to `Map<string, { artist: Artist, hype: HypeType }>`. The `Concert` entity type adds an `artist?: Artist` field instead of separate `logoUrl`/`logoColorProfile` fields.

## Risks / Trade-offs

- **localStorage size increase** → Acceptable for the expected artist count (<100). Monitor if onboarding adds batch-follow of hundreds.
- **Proto class in Aurelia templates** → Proto getter methods (`artist.name?.value`) are slightly more verbose than flat properties. Consider a thin value converter or computed property if templates become noisy.
- **Breaking existing tests** → Discovery and dashboard tests reference `ArtistBubble`/`FollowedArtist`. All test fixtures must be updated to use proto `Artist` instances.
