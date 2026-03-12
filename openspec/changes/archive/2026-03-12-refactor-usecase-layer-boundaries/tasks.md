## 1. Proto Schema (specification repo)

- [x] 1.1 Create `entity/v1/proximity.proto` with `Proximity` enum (UNSPECIFIED, HOME, NEARBY, AWAY)
- [x] 1.2 Add `optional double centroid_latitude` and `optional double centroid_longitude` fields to `Home` message in `user.proto`
- [x] 1.3 Rename `DateLaneGroup` to `ProximityGroup` in `concert_service.proto` (keep field name `away` — consistent with `PROXIMITY_AWAY` enum)
- [x] 1.4 Run `buf lint` and `buf format -w`, verify breaking changes are expected

## 2. Database Migration (backend repo)

- [x] 2.1 Add `centroid_latitude DOUBLE PRECISION` and `centroid_longitude DOUBLE PRECISION` columns to `homes` table in desired-state schema
- [x] 2.2 Generate Atlas migration with backfill for existing Japanese prefecture rows
- [x] 2.3 Validate migration locally with `atlas migrate apply --env local`

## 3. Entity Layer — Proximity Model (backend repo)

- [x] 3.1 Create `entity/proximity.go`: `Proximity` type, constants (`ProximityHome`, `ProximityNearby`, `ProximityAway`), `NearbyThresholdKm` constant
- [x] 3.2 Add `Latitude float64` and `Longitude float64` fields to `entity.Home` struct
- [x] 3.3 Create `pkg/geo/haversine.go` with `Haversine` function (move from `internal/geo`)
- [x] 3.4 Implement `Concert.ProximityTo(home *Home) Proximity` receiver method on entity
- [x] 3.5 Write unit tests for `Concert.ProximityTo` covering all scenarios (HOME, NEARBY, AWAY, nil home, nil venue, missing coordinates)

## 4. Entity Layer — Interface Extraction (backend repo)

- [x] 4.1 Define `PushNotificationSender` interface in entity layer
- [x] 4.2 Define `MerkleTreeBuilder` interface in entity layer
- [x] 4.3 Define `AdminAreaResolver` interface in entity layer
- [x] 4.4 Define `Cache` interface (in entity or usecase layer)
- [x] 4.5 Move event data types (`ConcertDiscoveredData`, `ScrapedConcertData`, `ConcertCreatedData`, `VenueCreatedData`, `ArtistCreatedData`) and subject constants from `infrastructure/messaging` to entity layer

## 5. Infrastructure — Interface Implementations (backend repo)

- [x] 5.1 Implement `PushNotificationSender` using `webpush-go` (move VAPID config and `http.Client` here)
- [x] 5.2 Implement `MerkleTreeBuilder` wrapping existing `infrastructure/merkle` package
- [x] 5.3 Implement `AdminAreaResolver` using the display name table from `internal/geo`
- [x] 5.4 Update `UserRepository.Create` and `UpdateHome` to resolve and persist centroid at write time
- [x] 5.5 Move centroid data table and `NormalizeAdminArea` to infrastructure

## 6. UseCase Layer Refactor (backend repo)

- [x] 6.1 Refactor `push_notification_uc.go`: inject `PushNotificationSender`, remove `webpush`/`net/http`/VAPID fields
- [x] 6.2 Refactor `concert_uc.go`: replace `groupByDateAndLane` with `entity.GroupByDateAndProximity` or direct `Concert.ProximityTo` calls, remove `geo` import
- [x] 6.3 Refactor `push_notification_uc.go`: replace `hasNearbyConcert` with `Concert.ProximityTo`, remove `geo` import
- [x] 6.4 Refactor `venue_enrichment_uc.go`: inject `AdminAreaResolver`, remove `geo` import
- [x] 6.5 Refactor `entry_uc.go`: inject `MerkleTreeBuilder`, remove `infrastructure/merkle` import
- [x] 6.6 Refactor `artist_uc.go`: inject `Cache` interface, remove `pkg/cache` concrete type import
- [x] 6.7 Refactor `artist_uc.go`, `concert_uc.go`, `concert_creation_uc.go`: use entity-layer event types, remove `infrastructure/messaging` import (keep `messaging.NewEvent` call only where `message.Publisher.Publish` is used)
- [x] 6.8 Update `ConcertCreationUseCase.CreateFromDiscovered` signature to use entity-layer type

## 7. DI Wiring (backend repo)

- [x] 7.1 Update Wire providers to inject new interfaces (`PushNotificationSender`, `MerkleTreeBuilder`, `AdminAreaResolver`, `Cache`)
- [x] 7.2 Run `wire` to regenerate DI code

## 8. Adapter Layer (backend repo)

- [x] 8.1 Update RPC mapper for `ProximityGroup` (was `DateLaneGroup`)
- [x] 8.2 Update concert handler for renamed response type

## 9. Cleanup (backend repo)

- [x] 9.1 Delete `internal/geo` package entirely
- [x] 9.2 Run `mockery` to regenerate mocks for new interfaces
- [x] 9.3 Update tests for refactored usecases (especially `NotifyNewConcerts` — now testable with mock sender)
- [x] 9.4 Run `make check` to verify lint + tests pass

## 10. UseCase Tests — Extracted Interface Coverage (backend repo)

- [x] 10.1 `push_notification_uc_test.go`: Sender returns `apperr.ErrNotFound` (410 Gone) → verify `DeleteByEndpoint` is called to clean up stale subscription
- [x] 10.2 `push_notification_uc_test.go`: `DeleteByEndpoint` fails after 410 Gone → verify error is logged but processing continues
- [x] 10.3 `push_notification_uc_test.go`: Sender returns transient error (Internal) → verify error is logged and remaining subscriptions are still processed
- [x] 10.4 `push_notification_uc_test.go`: Multiple subscriptions with mixed results (success, 410 Gone, transient error) → verify each is handled correctly
- [x] 10.5 `entry_uc_test.go`: `MerkleTreeBuilder.IdentityCommitment` returns error → verify error is wrapped and returned
- [x] 10.6 `entry_uc_test.go`: `MerkleTreeBuilder.Build` returns error → verify error is wrapped and returned
- [x] 10.7 `venue_enrichment_uc_test.go`: `UpdateEnriched` repository error → verify error propagation
- [x] 10.8 `venue_enrichment_uc_test.go`: `MergeVenues` repository error during duplicate merge → verify error propagation

## 11. Frontend (frontend repo)

- [x] 11.1 Update BSR packages to v0.24.0 (v1-compatible): `@buf/liverty-music_schema.bufbuild_es@1.10.0-20260312074833-163690671e3f.1`
- [x] 11.2 Update `DateLaneGroup` → `ProximityGroup` imports (field name `away` unchanged)
- [x] 11.3 Update dashboard concert grouping to use new type/field names
- [x] 11.4 Run `make check` to verify lint + tests pass
