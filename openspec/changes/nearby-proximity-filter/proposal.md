## Why

The `rename-passion-to-hype` change introduces `HYPE_TYPE_NEARBY` in the proto enum but leaves it unimplemented — the UI hides it and the backend falls back to ANYWHERE behavior. To complete the 4-tier hype system, the NEARBY tier needs a concrete proximity definition that determines which concerts are "close enough" to notify users about. Unlike HOME (exact ISO 3166-2 match), NEARBY requires physical distance calculation between the user's home area centroid and a concert venue's actual latitude/longitude, which is a fundamentally different kind of geographic filtering that does not yet exist in the system.

Additionally, the current dashboard lane classification ("home / nearby / away") is performed entirely in the frontend using a naive `admin_area` string comparison — any venue outside the user's home area is classified as "nearby" regardless of actual distance. The home/nearby/away classification is a shared domain concept used by both the dashboard and the notification filter, and should be computed by the backend as the single source of truth.

## What Changes

- Add latitude and longitude to venue records, populated during the existing venue enrichment pipeline from MusicBrainz coordinates and Google Places geometry
- Define a proximity model: compute Haversine distance between the user's home area centroid (from a static Go lookup of 47 Japanese prefecture centroids) and the venue's actual lat/lng, with a fixed 200km threshold
- Unify the home/nearby/away classification as backend domain logic, used by both the dashboard RPC and the notification filter
- **BREAKING**: Restructure `ListByFollowerResponse` from a flat concert list to date-grouped lane-classified groups (`DateLaneGroup[]`), each containing home/nearby/away concert lists
- Implement NEARBY filtering in `NotifyNewConcerts()` using the same proximity logic (replacing the current ANYWHERE fallback)
- Expose NEARBY as a selectable option in the frontend hype selector (currently hidden)

## Capabilities

### New Capabilities

- `nearby-proximity`: Definition of geographic proximity between a user's home area and a concert venue, including the Haversine distance model, venue lat/lng data source, home centroid lookup, and the classification interface used by both dashboard and notification filter

### Modified Capabilities

- `live-events`: `ListByFollower` response changes from flat `repeated Concert` to `repeated DateLaneGroup` with server-side date grouping and lane classification; Dashboard Lane Classification moves from frontend to backend
- `venue-normalization`: Enrichment pipeline extracts and persists venue latitude/longitude from MusicBrainz coordinates and Google Places geometry during enrichment

## Impact

- **specification**: `ListByFollowerResponse` restructured (breaking change); `Venue` entity gains optional `latitude`/`longitude` fields
- **backend**: New proximity classifier in `internal/geo`; venue entity and DB schema gain lat/lng; enrichment pipeline updated to extract coordinates; `ListByFollower` usecase performs date+lane grouping; `NotifyNewConcerts` uses proximity for NEARBY filtering
- **frontend**: Dashboard service simplified — removes `assignLane()` and `fetchUserHome()`, consumes pre-classified `DateLaneGroup[]` directly; hype selector shows 4 options
- **data**: Requires centroid coordinates for 47 Japanese prefectures (static Go map, sourced from Geospatial Information Authority of Japan)
