## Why

The backend usecase layer has accumulated direct dependencies on infrastructure packages (`webpush-go`, `infrastructure/messaging`, `infrastructure/merkle`) and a misplaced concrete implementation package (`internal/geo`). This makes pure business logic untestable in isolation and violates Clean Architecture's dependency rule. The most critical case is `push_notification_uc.go`, where `webpush.SendNotification` is called directly — making the notification delivery path completely untestable.

## What Changes

- **Define `Proximity` enum in proto** as the canonical domain concept for the geographic relationship between a user's home and a concert venue, replacing the UI-oriented "Lane" terminology.
- **BREAKING**: Rename `DateLaneGroup` to `ProximityGroup` in `concert_service.proto`, and rename its `away` field to `distant`.
- **Add centroid fields to `Home`** (proto message and DB schema) so that proximity classification becomes a pure entity function with no infrastructure dependency.
- **Move `ClassifyLane` logic to `Concert.ProximityTo(home)` receiver method** on the entity layer, replacing all `geo.ClassifyLane` calls in usecase.
- **Dissolve `internal/geo` package**: move `Haversine` to `pkg/geo`, move data tables (centroids, display names, normalization) to infrastructure, remove the package.
- **Extract `PushNotificationSender` interface** in entity layer, move `webpush` library usage to infrastructure, making `NotifyNewConcerts` fully testable.
- **Move `messaging` event types to entity layer** where they appear in usecase public interfaces (specifically `ConcertDiscoveredData` in `ConcertCreationUseCase`).
- **Extract `MerkleTreeBuilder` interface** in entity layer, move `infrastructure/merkle` direct calls out of `entry_uc.go`.
- **Replace `*cache.MemoryCache` concrete type** in `artistUseCase` with a `Cache` interface.
- **Move `AdminAreaResolver` behind an interface** for `DisplayName` used by `venue_enrichment_uc`.

## Capabilities

### New Capabilities

- `proximity-model`: Defines the `Proximity` enum in proto, `ProximityGroup` message, and the `Concert.ProximityTo()` entity method — the domain model for geographic closeness classification.

### Modified Capabilities

- `nearby-proximity`: Requirements change from "system SHALL maintain a centroid lookup" to "Home entity SHALL carry centroid coordinates populated at write time". `ClassifyLane` moves from a standalone function to a `Concert` receiver method.
- `user-home`: Home data model gains centroid fields (`centroid_latitude`, `centroid_longitude`) in both proto and DB schema. Centroid resolution happens at write time in the repository layer.
- `concert-service`: `DateLaneGroup` renamed to `ProximityGroup` with field rename `away` → `distant`. Response uses `Proximity` enum terminology.

## Impact

- **specification**: New `Proximity` enum, `Home` message change, `ProximityGroup` rename (breaking proto change).
- **backend/entity**: New `Proximity` type, `Concert.ProximityTo()` method, `Home` struct gains `Latitude`/`Longitude`, new interfaces (`PushNotificationSender`, `MerkleTreeBuilder`, `AdminAreaResolver`, `Cache`).
- **backend/usecase**: Remove all `infrastructure/*` and `internal/geo` imports. `ConcertCreationUseCase.CreateFromDiscovered` signature changes to use entity-layer types.
- **backend/infrastructure**: New implementations for extracted interfaces. Centroid resolution at `UpdateHome`/`Create` time. `webpush` adapter. `internal/geo` dissolved.
- **backend/pkg/geo**: New package with `Haversine` function.
- **backend/adapter**: Mapper updates for `ProximityGroup` rename.
- **frontend**: Adapt to `ProximityGroup` rename and `Proximity` enum (generated types change).
- **DB migration**: Add `centroid_latitude`/`centroid_longitude` columns to `homes` table, backfill existing rows.
- **backend/tests**: Add usecase tests exercising extracted interfaces (sender error paths, builder error paths, repository error propagation).
