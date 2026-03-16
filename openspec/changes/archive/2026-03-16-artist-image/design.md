## Context

The Artist entity has no image information; the frontend identifies artists only by name-hash HSL colors. fanart.tv is a community-driven artist image database that provides artist images (thumb, background, logo, banner) via a free API keyed by MusicBrainz ID (MBID).

The existing backend provides the following building blocks:
- `ARTIST.created` event (Watermill + NATS JetStream)
- Last.fm / MusicBrainz clients (throttle + retry pattern)
- concert-discovery CronJob (circuit breaker pattern)
- ArtistNameConsumer (event-driven async processing pattern)

## Goals / Non-Goals

**Goals:**
- Fetch artist image data from fanart.tv API by MBID and persist it in the database
- Fetch immediately on `ARTIST.created` events (for dashboard logo display during onboarding)
- Refresh and backfill image data via a periodic CronJob
- Include Fanart in the proto Artist message and return the best image per type via RPC

**Non-Goals:**
- Frontend image display implementation (separate change)
- Downloading and self-hosting image files (use fanart.tv URLs directly)
- Abstracting over image sources beyond fanart.tv

## Decisions

### 1. DB Storage: Single JSONB column

Store the fanart.tv API response in a `fanart` JSONB column as-is.

```sql
ALTER TABLE artists
    ADD COLUMN fanart JSONB,
    ADD COLUMN fanart_synced_at TIMESTAMPTZ;
```

**Why**: The fanart.tv response acts as an external cache. Normalizing into separate tables would make periodic update diff/upsert logic complex. JSONB allows full overwrite on refresh. Image selection logic (highest likes) is handled in Go.

**Alternatives considered**:
- `artist_images` normalized table: Could yield 10+ rows per artist. Diff logic on periodic refresh is complex. Every new image type requires schema changes.
- Per-type columns (`thumb_url`, `logo_url`): Locks best-image selection to the DB layer. Full candidate data is lost.

### 2. Entity Design: Mirror the fanart.tv structure directly

Treat fanart.tv as a first-class business concept rather than abstracting it. The entity field structure matches the fanart.tv API response exactly.

```go
type Fanart struct {
    ArtistThumb      []FanartImage `json:"artistthumb"`
    ArtistBackground []FanartImage `json:"artistbackground"`
    HDMusicLogo      []FanartImage `json:"hdmusiclogo"`
    MusicLogo        []FanartImage `json:"musiclogo"`
    MusicBanner      []FanartImage `json:"musicbanner"`
}

type FanartImage struct {
    ID    string `json:"id"`
    URL   string `json:"url"`
    Likes int    `json:"likes,string"`
    Lang  string `json:"lang"`
}
```

Add `Fanart *Fanart` and `FanartSyncTime *time.Time` to the `Artist` struct.

**Why**: JSONB-to-Go conversion is a single `json.Unmarshal` call. When fanart.tv adds new image types, only a new struct field is needed.

### 3. Proto: Generic `Url` message and Fanart

Consolidate `SourceUrl`, `FanartImageUrl`, and `OfficialSiteUrl` — three near-identical URL wrappers — into a single generic `Url` message.

```protobuf
// entity.proto
message Url {
    string value = 1 [(buf.validate.field).string = {
        uri: true
        min_len: 1
        max_len: 2048
    }];
}
// SourceUrl, FanartImageUrl, OfficialSiteUrl are removed
```

The Fanart message uses the consolidated `Url` type. Each field carries the best image (highest likes) URL for that image type.

```protobuf
// artist.proto
message Fanart {
    optional Url artist_thumb = 1;
    optional Url artist_background = 2;
    optional Url hd_music_logo = 3;
    optional Url music_logo = 4;
    optional Url music_banner = 5;
}

message OfficialSite {
    ...
    Url url = 2;  // was OfficialSiteUrl
}
```

```protobuf
// concert.proto
message Concert {
    ...
    Url source_url = 8;  // was SourceUrl
}
```

**Why**: All three URL wrappers have identical validation (URI + min/max). Field names carry the domain context, making type-level domain information redundant. Unifies them as a generic value type like `LocalDate` or `StartTime`. Source-breaking but wire-compatible; handled with the `buf skip breaking` label.

**Why (best image)**: The frontend does not need the full candidate list. Best-image selection is a backend responsibility. Logo fallback (`hd_music_logo ?? music_logo`) is handled on the frontend side.

### 4. Fetch Timing: Event Consumer + CronJob hybrid

| Mechanism | Trigger | Purpose |
|-----------|---------|---------|
| `ArtistImageConsumer` | `ARTIST.created` event | Immediate fetch (onboarding dashboard) |
| `artist-image-sync` CronJob | Daily schedule | Periodic refresh + backfill |

Both share the same `ArtistImageSyncUseCase` and fanart.tv client.

**Why**: The onboarding flow requires a logo to be available on the dashboard shortly after an artist is followed. A CronJob alone would introduce up to 24h delay.

### 5. fanart.tv Client: Follow existing patterns

Implemented with the same architecture as the Last.fm client.

- `infrastructure/music/fanarttv/client.go`
- `throttle.Throttler` for rate-limit control
- `backoff.Retry` for retries (exponential backoff, max 4 attempts)
- `httpx.IsRetryableStatus` for 429/503/504 retry targeting
- API key sourced from `FANARTTV_API_KEY` environment variable
- Implements `entity.ArtistImageResolver` interface

### 6. Best Image Selection: Highest likes

```go
func BestByLikes(images []FanartImage) string {
    // Returns the URL of the image with the highest likes count.
    // Returns empty string for an empty slice.
}
```

Defined as an entity-layer function and called from the mapper layer.

### 7. CronJob Design: Follow concert-discovery pattern

- `cmd/job/artist-image-sync/main.go`
- DI via `di.InitializeImageSyncJobApp()`
- Target selection: `fanart IS NULL OR fanart_synced_at < now() - 7d` (NULL prioritized)
- Circuit breaker: stop after 3 consecutive failures
- Exit 0 (prevent K8s restart)
- K8s CronJob manifest (templated from concert-discovery)

## Risks / Trade-offs

**[No fanart.tv data for an artist]** — Artist.Fanart remains empty. The frontend falls back to the existing HSL color (no regression). Coverage may be low for indie/local artists.

**[fanart.tv API downtime]** — Controlled by retry + circuit breaker. Image absence does not affect the core service function (concert notifications).

**[fanart.tv ToS change or shutdown]** — Existing JSONB data is preserved. Migration to another source requires only replacing the `ArtistImageResolver` implementation.

**[JSONB column size]** — Approximately a few KB per artist (list of image URLs). No concern at tens-of-thousands scale.
