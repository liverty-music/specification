## Context

The backend follows Clean Architecture with four layers: Entity, UseCase, Adapter, Infrastructure. Over time, several usecase files have accumulated direct imports from `internal/infrastructure/` and `internal/geo/`, violating the dependency rule (inner layers must not depend on outer layers). The most impactful violation is `push_notification_uc.go` calling `webpush.SendNotification` directly, making notification delivery untestable.

A misplaced `internal/geo` package contains both business rules (lane classification) and infrastructure concerns (hardcoded centroid data, display name tables). The classification logic itself is a domain concept that belongs on the `Concert` entity, while the data tables belong in infrastructure.

This change is cross-repo: proto schema changes in specification must be released before backend can consume the new generated types.

## Goals / Non-Goals

**Goals:**
- Eliminate all `internal/infrastructure/*` and `internal/geo` imports from usecase layer
- Make every usecase method testable with mocks alone (no real HTTP, no real webpush)
- Establish `Proximity` as the canonical domain concept replacing UI-oriented "Lane"
- Move `Home` centroid resolution to write-time, eliminating runtime data lookups in business logic

**Non-Goals:**
- HypeType ANYWHERE → AWAY rename (separate change)
- Adding non-Japanese centroid data (Phase 2)
- Changing the event-driven architecture (Watermill `message.Publisher` stays as-is)
- Refactoring `message.Publisher` — it is already an abstract interface

## Decisions

### 1. `Proximity` as proto enum + `Concert.ProximityTo()` as entity receiver

**Decision**: Define `Proximity` enum in `entity/v1/proximity.proto`. Implement classification as `func (c *Concert) ProximityTo(home *Home) Proximity` in Go entity layer.

**Why**: The classification is a domain concept (how close is this concert to the user?). Making it a `Concert` receiver encapsulates nil-guard logic for both `home` and `venue`, and reads naturally: `c.ProximityTo(user.Home)`.

**Alternative considered**: Package-level function `ClassifyProximity(home, venue)` — rejected because it forces nil checks at every call site.

### 2. Centroid on `Home` entity (write-time resolution)

**Decision**: Add `centroid_latitude DOUBLE PRECISION` and `centroid_longitude DOUBLE PRECISION` to the `homes` table. Populate at write time in `UserRepository.Create` / `UpdateHome`. The `Home` entity gains `Latitude float64` and `Longitude float64` fields.

**Why**: This eliminates the need for a `GeoDataProvider` interface at read time. `Concert.ProximityTo()` becomes a pure function over entity fields — no interface injection, no data lookups.

**Centroid resolution strategy**: The repository layer uses an internal centroid table (same data as current `geo.prefectureCentroids`) to resolve `level_1` → `(latitude, longitude)` during write. This is an infrastructure implementation detail invisible to usecase/entity layers.

**Backfill**: A DB migration backfills existing `homes` rows using the same centroid lookup.

### 3. `ProximityGroup` replaces `DateLaneGroup`

**Decision**: Rename `DateLaneGroup` to `ProximityGroup` in `concert_service.proto`. Keep field name `away` (consistent with `PROXIMITY_AWAY` enum value).

**Why**: "Lane" is a UI presentation concept. "Proximity" is the domain concept. The field name `away` is retained because it matches the `PROXIMITY_AWAY` enum value — consistency between enum and field names is more important than avoiding reuse of the old message's field name.

**Breaking change handling**: This is a breaking proto change. The specification PR will use the `buf skip breaking` label.

### 4. `PushNotificationSender` interface

**Decision**: Define in entity layer:

```go
type PushNotificationSender interface {
    Send(ctx context.Context, payload []byte, sub *PushSubscription) error
}
```

Infrastructure implements this using `webpush-go` with VAPID credentials and `http.Client`. The sender returns `apperr` errors: `apperr.ErrNotFound` for 410 Gone (subscription expired), `codes.Internal` for delivery failures. This keeps HTTP status code semantics in infrastructure while the usecase handles domain-level error classification (e.g., delete stale subscription on NotFound).

**Why**: The usecase currently holds `vapidPublicKey`, `vapidPrivate`, `vapidContact`, and `*http.Client` — all infrastructure concerns. Extracting a sender interface moves all of this to infrastructure while keeping the business logic (410 Gone cleanup, per-subscription error handling) in usecase where it belongs.

### 5. Event data types to entity layer

**Decision**: Move `messaging.ConcertDiscoveredData`, `messaging.ScrapedConcertData`, `messaging.ConcertCreatedData`, `messaging.VenueCreatedData`, and `messaging.ArtistCreatedData` from `infrastructure/messaging` to `entity/` as pure data structs.

Move event subject constants (`SubjectConcertDiscovered`, etc.) alongside them.

Keep `messaging.NewEvent()` factory in infrastructure (it creates Watermill `message.Message`).

**Why**: `ConcertCreationUseCase.CreateFromDiscovered(ctx, data messaging.ConcertDiscoveredData)` has an infrastructure type in its public interface. The data structs are just DTOs with no infrastructure dependency — they belong in entity.

### 6. `MerkleTreeBuilder` interface

**Decision**: Define in entity layer:

```go
type MerkleTreeBuilder interface {
    IdentityCommitment(userID []byte) ([]byte, error)
    Build(eventID string, leaves [][]byte) (nodes []MerkleNode, root []byte, err error)
}
```

`entry_uc.go` calls this interface instead of `merkle.IdentityCommitment()` and `merkle.NewBuilder()`.

**Why**: Poseidon hash implementation is an infrastructure concern. The usecase should only know "compute commitment" and "build tree", not which hash function is used.

### 7. `AdminAreaResolver` interface

**Decision**: Define in entity layer:

```go
type AdminAreaResolver interface {
    DisplayName(code, lang string) string
}
```

`venue_enrichment_uc.go` uses this instead of `geo.DisplayName()`.

`NormalizeAdminArea` stays in infrastructure — it's only called from `infrastructure/gcp/gemini/searcher.go`.

### 8. `Cache` interface for artist usecase

**Decision**: Define in entity layer or usecase layer:

```go
type Cache interface {
    Get(key string) any
    Set(key string, value any)
}
```

Replace `*cache.MemoryCache` concrete type in `artistUseCase` struct.

### 9. `Haversine` to `pkg/geo`

**Decision**: Move `Haversine` function to `pkg/geo/haversine.go`. It's a pure math function with no external dependencies — `pkg/` is the correct home for cross-layer utilities.

### 10. Dissolve `internal/geo`

**Decision**: After all functions are relocated, delete the `internal/geo` package entirely.

Destination for each function:
| Function | Destination |
|---|---|
| `ClassifyLane` | entity `Concert.ProximityTo()` |
| `Lane` type + constants | entity `Proximity` type |
| `NearbyThresholdKm` | entity constant |
| `Haversine` | `pkg/geo` |
| `PrefectureCentroid` | infrastructure (internal to repo, used at write-time) |
| `DisplayName` | infrastructure (behind `AdminAreaResolver` interface) |
| `NormalizeAdminArea` | infrastructure (already only used there) |

## Risks / Trade-offs

**[Risk] Backfill migration for centroid columns** → Centroid data is static and well-known (47 Japanese prefectures). Migration uses a VALUES list to UPDATE existing rows. Reversible with a simple `ALTER TABLE DROP COLUMN`.

**[Risk] Breaking proto change (DateLaneGroup → ProximityGroup)** → Frontend and backend must be updated together after BSR gen. Use `buf skip breaking` label on specification PR. Frontend impact is limited to type imports and field names in the concert list view.

**[Risk] Many interfaces extracted at once** → Each interface is small (1-3 methods) and has a single implementation. The risk of over-abstraction is low because every extraction is motivated by a concrete testability problem. Each can be implemented and tested independently.

**[Trade-off] Event data types in entity layer** → These DTOs are not "core business entities" in the purest sense, but they appear in usecase public interfaces. Placing them in entity is pragmatic — the alternative (a separate `usecase/dto` package) adds a layer without clear benefit.
