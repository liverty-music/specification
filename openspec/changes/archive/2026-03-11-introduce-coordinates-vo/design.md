## Context

Geographic coordinates currently exist as raw `optional double` fields in proto (`centroid_latitude`, `centroid_longitude` on `Home`) and flat struct fields in Go entities (`Latitude *float64`, `Longitude *float64` on `Venue`; `Latitude float64`, `Longitude float64` on `Home`). This is inconsistent with the project convention of wrapping every domain concept in a dedicated type. It also allows structurally invalid states — one coordinate present without the other.

The `refactor-usecase-layer-boundaries` change recently introduced the centroid fields and renamed `Lat`/`Lng` to `Latitude`/`Longitude`, but did not address the missing VO abstraction.

## Goals / Non-Goals

**Goals:**
- Introduce a shared `Coordinates` VO usable by `Home` (centroid), `Venue` (location), and `VenuePlace` (search result)
- Eliminate structurally invalid states (lat without lng)
- Align proto and Go entity representations

**Non-Goals:**
- Adding `Coordinates` to `venue.proto` — proto venue fields are out of scope; the Venue proto currently has no coordinate fields and adding them is a separate concern
- Database schema changes — DB columns remain flat (`centroid_latitude`, `centroid_longitude`, `latitude`, `longitude`); Repository layer handles mapping
- Adding validation constraints to `Coordinates` — raw WGS 84 values including 0.0 are valid

## Decisions

### Decision 1: Single `Coordinates` message in `entity/v1/`

Place `Coordinates` in a new file `entity/v1/coordinates.proto` alongside other entity types.

**Alternative**: Define it inside `user.proto` as a nested message → rejected because `Venue` and other entities also need coordinates.

### Decision 2: `Home.centroid` as `optional Coordinates`

Replace `optional double centroid_latitude = 4` and `optional double centroid_longitude = 5` with `optional Coordinates centroid = 4`. Field number 4 reused; field 5 marked `reserved`.

**Alternative**: Keep flat fields → rejected because it violates the type-safe wrapper convention and allows half-populated state.

### Decision 3: Go entity `*Coordinates` for optional, value `Coordinates` for required

- `Home.Centroid *Coordinates` — nil when centroid cannot be resolved (unsupported country)
- `Venue.Coordinates *Coordinates` — nil until enrichment populates coordinates
- `VenuePlace.Coordinates *Coordinates` — nil when external service returns no coordinates

### Decision 4: Infrastructure `LatLng` struct renamed to `Coordinates`

The `infrastructure/geo/centroid.go` already has a `LatLng` struct with `Latitude`/`Longitude` fields. Rename to `Coordinates` to match the entity type name, keeping the infrastructure struct separate (infra returns its own type, repository maps to entity).

**Alternative**: Use `entity.Coordinates` directly in infrastructure → rejected because infrastructure should not import entity layer.

### Decision 5: DB columns unchanged

DB columns stay as `centroid_latitude`/`centroid_longitude` (homes) and `latitude`/`longitude` (venues). Repository layer maps between flat columns and `*entity.Coordinates`. No migration needed.

## Risks / Trade-offs

- **Breaking proto change** → Mitigated: branch is unreleased, `buf skip breaking` label on PR.
- **Field number reuse in Home** → Field 4 changes type from `double` to `Coordinates` message. Safe because branch is unreleased and no data exists with the old schema.
- **Increased indirection** → `home.Centroid.Latitude` vs `home.Latitude`. Acceptable trade-off for type safety and consistency.
