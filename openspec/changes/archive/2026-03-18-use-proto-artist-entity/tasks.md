## 1. Entity Layer — Replace custom interfaces with proto types

- [x] 1.1 Update `src/entities/artist.ts`: re-export proto `Artist`, `Fanart`, `LogoColorProfile` from BSR package. Add helper functions (`bestLogoUrl(artist)`, `bestBackgroundUrl(artist)`) that encapsulate `BestByLikes`-equivalent logic
- [x] 1.2 Update `src/entities/follow.ts`: redefine `FollowedArtist` as `{ artist: Artist, hype: Hype }`. Remove `LogoColorProfile` interface (use proto type). Keep `Hype` type union
- [x] 1.3 Update `src/entities/concert.ts`: replace `logoUrl`, `backgroundUrl`, `logoColorProfile` fields with `artist?: Artist`. Keep all other concert fields unchanged

## 2. State Layer — Store proto Artist in guest state

- [x] 2.1 Update `src/state/app-state.ts`: replace `GuestFollow` interface with `{ artist: Artist, home: string | null }` in `GuestState.follows`. Remove `GuestFollow` type
- [x] 2.2 Update `src/state/middleware.ts`: serialize guest follows using `Artist.toJsonString()`, deserialize using `fromJson(ArtistSchema, ...)`
- [x] 2.3 Update reducer actions: `guest/follow` action payload changes from `{ artistId, name }` to `{ artist: Artist }`. Update `guest/unfollow` to use `artist.id?.value`

## 3. Service Layer — Pass proto Artist through without mapping

- [x] 3.1 Update `src/services/artist-service-client.ts`: remove `toBubble()` function and `ArtistBubble` interface. Return proto `Artist[]` from `listTop()`, `listSimilar()`, `search()`
- [x] 3.2 Update `src/services/follow-service-client.ts`: `listFollowed()` returns `FollowedArtist[]` with proto `Artist` objects. Onboarding path returns guest store artists. Backend path passes `fa.artist` through directly. Remove `listFollowedAsBubbles()` (merge with `listFollowed`)
- [x] 3.3 Update `src/services/dashboard-service.ts`: `artistMap` becomes `Map<string, { artist: Artist, hype: HypeType }>`. `protoConcertToEntity()` receives `Artist` instead of separate `logoUrl`/`backgroundUrl`/`logoColorProfile` parameters
- [x] 3.4 Update `src/services/local-artist-client.ts`: adapt to new `FollowedArtist` shape
- [x] 3.5 Update `src/services/guest-data-merge-service.ts`: read `artist.id?.value` from stored proto Artist objects

## 4. Discovery Components — Use PhysicsBubble composition

- [x] 4.1 Define `PhysicsBubble` type (`{ artist: Artist, x, y, radius }`) in `src/components/dna-orb/` or `src/entities/`
- [x] 4.2 Update `src/components/dna-orb/dna-orb-canvas.ts` and `bubble-physics.ts`: replace `ArtistBubble` references with `PhysicsBubble`
- [x] 4.3 Update `src/routes/discovery/bubble-manager.ts`: construct `PhysicsBubble` from proto `Artist` (assign `x`, `y`, `radius` as physics properties)
- [x] 4.4 Update `src/routes/discovery/follow-orchestrator.ts`: dispatch `guest/follow` with proto `Artist` instead of `{ artistId, artistName }`
- [x] 4.5 Update `src/routes/discovery/discovery-route.ts`, `genre-filter-controller.ts`, `search-controller.ts`: replace `ArtistBubble` with `PhysicsBubble` or `Artist`
- [x] 4.6 Update `src/services/bubble-pool.ts`: adapt to `PhysicsBubble` type

## 5. Dashboard & My Artists — Consume proto Artist

- [x] 5.1 Update `src/components/live-highway/event-card.html`: bind `artist-color` profile from `event.artist?.fanart?.logoColorProfile` instead of `event.logoColorProfile`. Derive `logoUrl` from `event.artist`
- [x] 5.2 Update `src/custom-attributes/artist-color.ts`: accept proto `LogoColorProfile` type from BSR package
- [x] 5.3 Update `src/routes/my-artists/my-artists-route.ts`: consume `FollowedArtist` with proto `Artist` object
- [x] 5.4 Update `src/components/live-highway/event-detail-sheet.html` and `.ts`: adapt to `Concert.artist` field

## 6. Cleanup & Verification

- [x] 6.1 Delete unused files and exports: remove `ArtistBubble` interface, `toBubble()`, flattened `FollowedArtist` mapping code, `LogoColorProfile` custom interface
- [x] 6.2 Run `make check` (lint + test) and fix any type errors or test failures
- [x] 6.3 Verify onboarding flow: follow artist during discovery → dashboard shows logo + color profile
- [x] 6.4 Verify authenticated flow: login → dashboard shows logo + color profile from ListFollowed
