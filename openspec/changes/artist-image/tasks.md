## 1. Proto (specification repo)

- [x] 1.1 Add `FanartImageUrl` wrapper message to `entity/v1/entity.proto` with URI validation
- [x] 1.2 Add `Fanart` message to `entity/v1/artist.proto` with optional fields: `artist_thumb`, `artist_background`, `hd_music_logo`, `music_logo`, `music_banner`
- [x] 1.3 Add `optional Fanart fanart` field to `Artist` message
- [x] 1.4 Run `buf lint` and `buf format -w` to validate

## 2. Database Migration (backend repo)

- [x] 2.1 Add `fanart JSONB` and `fanart_synced_at TIMESTAMPTZ` columns to `artists` table in `schema.sql`
- [x] 2.2 Generate Atlas migration with `atlas migrate diff --env local add-artist-fanart`
- [x] 2.3 Add migration file to `k8s/atlas/base/kustomization.yaml`

## 3. Entity Layer (backend repo)

- [x] 3.1 Add `Fanart` and `FanartImage` structs to `internal/entity/` with JSON tags matching fanart.tv field names
- [x] 3.2 Add `Fanart *Fanart` and `FanartSyncTime *time.Time` fields to `Artist` struct
- [x] 3.3 Implement `BestByLikes([]FanartImage) string` function
- [x] 3.4 Define `ArtistImageResolver` interface with `ResolveImages(ctx, mbid) (*Fanart, error)`
- [x] 3.5 Add `UpdateFanart(ctx, id, fanart, syncTime)` method to `ArtistRepository` interface

## 4. Infrastructure: fanart.tv Client (backend repo)

- [x] 4.1 Create `internal/infrastructure/music/fanarttv/client.go` implementing `ArtistImageResolver`
- [x] 4.2 Implement `GET /v3/music/{mbid}` with throttle, retry, and error handling (follow lastfm client pattern)
- [x] 4.3 Handle HTTP 404 as nil return (no images), HTTP 429 with retry
- [x] 4.4 Add `FANARTTV_API_KEY` to `pkg/config/config.go`

## 5. Infrastructure: Database Repository (backend repo)

- [x] 5.1 Implement `UpdateFanart` in `artist_repo.go` (UPDATE fanart JSONB and fanart_synced_at)
- [x] 5.2 Update existing artist query methods to include `fanart` and `fanart_synced_at` columns
- [x] 5.3 Add `ListStaleOrMissingFanart(ctx, staleDuration, limit)` query for CronJob

## 6. UseCase Layer (backend repo)

- [x] 6.1 Create `ArtistImageSyncUseCase` with `SyncArtistImage(ctx, artistID, mbid)` method
- [x] 6.2 Implement: resolve images → update fanart (or sync time only if nil) flow

## 7. Event Consumer (backend repo)

- [x] 7.1 Create `ArtistImageConsumer` in `internal/adapter/event/` subscribing to `ARTIST.created`
- [x] 7.2 Wire consumer into `cmd/consumer/main.go` router
- [x] 7.3 Update DI in `internal/di/consumer.go`

## 8. CronJob (backend repo)

- [x] 8.1 Create `cmd/job/artist-image-sync/main.go` (follow concert-discovery pattern)
- [x] 8.2 Implement batch processing with circuit breaker (3 consecutive failures)
- [x] 8.3 Add DI initializer `InitializeImageSyncJobApp` in `internal/di/`

## 9. RPC Mapper (backend repo)

- [x] 9.1 Update `internal/adapter/rpc/mapper/artist.go` to map `Fanart` entity → proto using `BestByLikes`

## 10. Kubernetes Manifests (cloud-provisioning repo)

- [x] 10.1 Create `artist-image-sync` CronJob manifest (template from concert-discovery)
- [x] 10.2 Add `FANARTTV_API_KEY` to ExternalSecret / Secret configuration
- [x] 10.3 Mount API key env var in both consumer Deployment and CronJob

## 11. Tests (backend repo)

- [x] 11.1 Unit test `BestByLikes` function
- [x] 11.2 Unit test fanart.tv client with httptest server
- [x] 11.3 Integration test `UpdateFanart` and `ListStaleOrMissingFanart` repository methods
- [x] 11.4 Unit test `ArtistImageConsumer` handler
- [ ] 11.5 Unit test proto mapper with fanart data (blocked: requires BSR-generated types)
