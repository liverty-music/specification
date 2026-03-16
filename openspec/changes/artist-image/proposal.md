## Why

Artist cards (my-artists page, dashboard concert cards) and logo displays (dashboard) have no images. The frontend currently uses name-hash HSL colors as the only visual identifier, but fans need recognizable artist images and logos for intuitive identification. The fanart.tv API provides community-curated artist images keyed by MusicBrainz ID, leveraging our existing MBID data.

## What Changes

- Add fanart.tv image data (Fanart) to the Artist entity
- Implement a fanart.tv API client in the backend (following the existing Last.fm / MusicBrainz client pattern)
- Fetch images asynchronously on `ARTIST.created` events (needed for dashboard logo display during onboarding)
- Run a periodic CronJob (`artist-image-sync`) for image refresh and backfill
- Add a Fanart message to the proto Artist message; the mapper selects the best image (highest likes) per type
- Add `fanart` (JSONB) and `fanart_synced_at` (TIMESTAMPTZ) columns to the artists table
- Consolidate `SourceUrl`, `FanartImageUrl`, and `OfficialSiteUrl` into a generic `Url` message

## Capabilities

### New Capabilities

- `artist-image`: Fetch, store, and serve artist images (thumb, background, logo, banner) from fanart.tv

### Modified Capabilities

- `artist-service-infrastructure`: Add Fanart field to Artist entity and UpdateFanart operation to ArtistRepository

## Impact

- **Proto**: Add `Fanart` message to `liverty_music.entity.v1.Artist` + consolidate `SourceUrl`/`FanartImageUrl`/`OfficialSiteUrl` into `Url` (source-breaking, wire-compatible; requires `buf skip breaking` label)
- **Backend**: Changes across entity, usecase, adapter/event, adapter/rpc/mapper, infrastructure/music/fanarttv, infrastructure/database/rdb, cmd/job, and di layers
- **DB**: Column addition migration on artists table
- **K8s**: Add artist-image-sync CronJob manifests and FANARTTV_API_KEY Secret/ConfigMap management
- **Frontend**: Out of scope (separate change)
