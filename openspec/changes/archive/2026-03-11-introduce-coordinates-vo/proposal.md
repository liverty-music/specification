## Why

Geographic coordinates (latitude/longitude) appear as raw `double` fields in proto and flat struct fields in Go entities across `Home` and `Venue`. This violates the project's type-safe wrapper convention — every other domain concept uses a dedicated message/struct. The raw fields also allow structurally invalid states (e.g., latitude present but longitude absent).

## What Changes

- **Proto**: Introduce a `Coordinates` message in `entity/v1/` with `double latitude` and `double longitude` fields. Replace raw `optional double centroid_latitude`/`centroid_longitude` on `Home` with `optional Coordinates centroid`. **BREAKING**
- **Go Entity**: Introduce `entity.Coordinates` struct. Replace `Home.Latitude`/`Home.Longitude` with `Home.Centroid *Coordinates`. Replace `Venue.Latitude`/`Venue.Longitude` and `VenuePlace.Latitude`/`VenuePlace.Longitude` with `*Coordinates` fields.
- **Infrastructure**: Update repository mappers to convert between flat DB columns and `*Coordinates`.
- **Spec docs**: Update `user-home`, `nearby-proximity`, and `venue-normalization` specs to reference `Coordinates` VO.

## Capabilities

### New Capabilities

- `coordinates-vo`: Shared `Coordinates` value object for representing geographic latitude/longitude pairs across the domain model.

### Modified Capabilities

- `user-home`: `Home` proto message and Go entity use `Coordinates` instead of raw fields.
- `nearby-proximity`: Proximity classification references `Home.Centroid` coordinates via `Coordinates` VO.
- `venue-normalization`: Venue coordinate storage uses `Coordinates` VO in Go entity.

## Impact

- **Proto** (`entity/v1/user.proto`): Breaking field change on `Home` message — unreleased branch, `buf skip breaking` label required.
- **Go Entity** (`entity/`): `Home`, `Venue`, `VenuePlace` struct field changes — all consumers must update.
- **Infrastructure** (`database/rdb/`, `maps/google/`, `infrastructure/geo/`): Repository and mapper code updates for `*Coordinates` conversion.
- **UseCase** (`usecase/`): `Concert.ProximityTo` and any code accessing `Home.Latitude`/`Longitude` must use `Centroid` field.
- **Adapter** (`adapter/rpc/mapper/`): Proto-to-entity mapping for `Home.centroid` and `Venue` coordinates.
- **Tests**: Entity and usecase tests referencing coordinate fields must update.
