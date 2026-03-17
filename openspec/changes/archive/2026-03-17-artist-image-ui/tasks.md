## 0. Backend: Include Fanart in ListFollowed Response

- [x] 0.1 Update `followListByUserQuery` in `follow_repo.go` to LEFT JOIN `artist_fanart` table and scan fanart columns into `entity.Artist.Fanart`
- [x] 0.2 Add/update integration test for `ListByUser` to verify fanart fields are populated when present and nil when absent
- [x] 0.3 Run `make check` in backend

## 1. Data Layer: Fanart URL Propagation (Frontend)

- [x] 1.1 Add `logoUrl?`, `backgroundUrl?`, `thumbUrl?` fields to `FollowedArtistInfo` interface in `follow-service-client.ts`
- [x] 1.2 Map `artist.fanart` fields to `FollowedArtistInfo` in `listFollowed()` with logo fallback chain (`hd_music_logo?.value ?? music_logo?.value`)
- [x] 1.3 Add `logoUrl?`, `backgroundUrl?` fields to `LiveEvent` interface in `live-event.ts`
- [x] 1.4 Add `thumbUrl?`, `logoUrl?` fields to `FollowedArtist` interface in `my-artists-route.ts`
- [x] 1.5 Map fanart URLs from `FollowedArtistInfo` to `FollowedArtist` in `my-artists-route.ts` loading()
- [x] 1.6 Build a `Map<string, FanartUrls>` from ListFollowed response in the dashboard service and enrich `LiveEvent` objects with `logoUrl` and `backgroundUrl`

## 2. Event Card: Logo Image

- [x] 2.1 Update `event-card.html` template: conditional `<img>` for logo with `<span>` fallback for text
- [x] 2.2 Add logo image CSS in `event-card.css`: `object-fit: contain`, `max-block-size`, `loading="lazy"`, `decoding="async"`
- [x] 2.3 Handle image load error: fall back to text display on `error` event

## 3. Event Detail Sheet: Hero Background Image

- [x] 3.1 Update `event-detail-sheet.html`: add conditional `sheet-hero` div above `sheet-artist-header` when `backgroundUrl` exists
- [x] 3.2 Add hero CSS in `event-detail-sheet.css`: `aspect-ratio: 16/9`, `object-fit: cover`, gradient fade at bottom edge
- [x] 3.3 Pass `backgroundUrl` to event-detail-sheet component (already on LiveEvent via task 1.3)

## 4. My Artists Grid: Thumbnail Background

- [x] 4.1 Update `my-artists-route.html` grid tile: add inline `background-image` style when `thumbUrl` exists
- [x] 4.2 Add thumbnail background CSS in `my-artists-route.css`: ensure gradient overlay remains on top for text readability
- [x] 4.3 Handle thumbnail load error: clear background-image to fall back to gradient

## 5. Verification

- [x] 5.1 Visual verification: event cards show logo for artists with fanart, text for others
- [x] 5.2 Visual verification: detail sheet shows hero image when background exists
- [x] 5.3 Visual verification: grid tiles show thumbnail when available, gradient when not
- [x] 5.4 Run `make check` (lint + test) — all lint passes, 607 unit tests pass, E2E timeouts are pre-existing
- [x] 5.5 E2E tests for 5.1–5.3 (6/6 pass with mock RPC data in `e2e/artist-image-ui.spec.ts`)
- [x] 5.6 Add `https://assets.fanart.tv` to CSP `img-src` in `index.html` for production fanart.tv images
