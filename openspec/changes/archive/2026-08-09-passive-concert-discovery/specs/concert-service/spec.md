## ADDED Requirements

### Requirement: ListByLocation RPC

The system SHALL provide an unauthenticated RPC `ConcertService.ListByLocation` that accepts a `GeoLocation` reference point and a date range, returning all concerts in the DB whose venues are HOME or NEARBY relative to the reference point, grouped by date and proximity.

#### Scenario: Successful proximity-grouped listing

- **WHEN** `ListByLocation` is called with a valid `GeoLocation` and a `from`/`to` date range
- **THEN** it SHALL return concerts grouped by date using `ProximityGroup` messages
- **AND** each `ProximityGroup` SHALL contain concerts classified into `home` and `nearby` fields based on `Concert.ProximityTo(GeoLocation)`
- **AND** the `away` field SHALL always be empty (AWAY concerts are excluded from the response)
- **AND** each concert SHALL include a resolved `Venue` with `name`, `admin_area`, and coordinates
- **AND** each concert SHALL include `listed_venue_name` with the raw scraped venue name
- **AND** groups SHALL be ordered by date ascending

#### Scenario: Date range validation — range exceeds 30 days

- **WHEN** `ListByLocation` is called with `to - from > 30 days`
- **THEN** it SHALL return an `INVALID_ARGUMENT` error via protovalidate

#### Scenario: Date range validation — from after to (inverted range)

- **WHEN** `ListByLocation` is called with `from > to` (e.g., `from = 2026-08-15, to = 2026-08-01`)
- **THEN** it SHALL return an `INVALID_ARGUMENT` error
- **AND** the validation SHALL be enforced via a CEL cross-field constraint on `ListByLocationRequest` (`message_level cel: "this.from <= this.to"`) because `to - from` is negative and the 30-day check alone does not catch inverted ranges

#### Scenario: No concerts found

- **WHEN** `ListByLocation` is called with a valid request
- **AND** no concerts exist within 200 km of the reference point in the given date range
- **THEN** it SHALL return an empty `groups` list without error

#### Scenario: GeoLocation HOME classification

- **WHEN** a concert's venue `admin_area` matches `location.admin_area`
- **THEN** the concert SHALL be classified as HOME regardless of Haversine distance

#### Scenario: GeoLocation NEARBY classification

- **WHEN** a concert's venue `admin_area` does not match `location.admin_area`
- **AND** the Haversine distance between `(location.latitude, location.longitude)` and the venue coordinates is ≤ 200 km
- **THEN** the concert SHALL be classified as NEARBY

#### Scenario: AWAY concerts excluded

- **WHEN** a concert's venue is beyond 200 km from the reference point and has a different `admin_area`
- **THEN** the concert SHALL NOT appear in the response

#### Scenario: Unauthenticated access

- **WHEN** `ListByLocation` is called without authentication headers
- **THEN** it SHALL return a valid response (no `UNAUTHENTICATED` error)

#### Scenario: ConcertRepository.ListByLocation query

- **WHEN** the use case calls the repository layer
- **THEN** the repository SHALL execute a query filtering `e.local_event_date BETWEEN $from AND $to`
- **AND** the query SHALL pre-filter venues using a bounding box (`v.latitude BETWEEN (location.latitude - 1.8) AND (location.latitude + 1.8)`, `v.longitude BETWEEN (location.longitude - 2.6) AND (location.longitude + 2.6)`) to avoid full-table scans; the longitude margin of ±2.6° is conservative enough to cover 200 km at all latitudes in Japan including Hokkaido (43°N+); the ±2.3° value is insufficient above 38.6°N
- **AND** the bounding box pre-filter SHALL include all venues whose `admin_area` matches `location.admin_area` regardless of coordinates
- **AND** final Haversine filtering to 200 km SHALL be applied in the Go use-case layer on bounding-box candidates by calling `entity.GroupByDateAndProximity`; since that function accepts `*entity.Home`, the use case SHALL construct a transient `entity.Home{Level1: location.AdminArea, Centroid: &entity.Coordinates{Latitude: location.Latitude, Longitude: location.Longitude}}` as the proximity reference — this adapter is the responsibility of the use-case layer, not the entity layer
- **AND** AWAY-tier `ProximityGroup` entries (where `len(Home)+len(Nearby)==0` after classification) SHALL be stripped from the result before returning; entire date-group entries with no HOME or NEARBY concerts SHALL be omitted, not returned as empty rows

---

## RENAMED Requirements

### Requirement: List Concerts with Proximity for Unauthenticated Users

FROM: `ListWithProximity`
TO: `ListByArtists`

The RPC signature, parameter types, and behavior are unchanged. Only the RPC name changes. The rename reflects that the primary filter axis is `artist_ids`, not proximity; proximity grouping is a feature of the response format, not the filter.

#### Scenario: Existing behavior preserved after rename

- **WHEN** `ListByArtists` is called with one or more `artist_ids` and a valid `Home`
- **THEN** it SHALL behave identically to the former `ListWithProximity`
- **AND** return `ProximityGroup[]` grouped by date and classified by proximity to `home`
