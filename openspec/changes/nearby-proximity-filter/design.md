## Context

The Liverty Music platform notifies users about upcoming concerts for artists they follow. Each user sets a "hype level" per artist (WATCH / HOME / NEARBY / ANYWHERE) that controls notification scope and dashboard rendering. The `HYPE_TYPE_NEARBY` enum value exists in proto but is unimplemented — the backend treats it as ANYWHERE and the frontend hides it.

The dashboard displays concerts in a three-lane highway UI (home / nearby / away) grouped by date. Currently, lane classification is performed entirely in the frontend by comparing `venue.admin_area` against `user.home.level_1` (ISO 3166-2 code equality). This is inaccurate: a concert in Fukuoka is classified as "nearby" for a Tokyo user, even though it is 900km away.

Venues are created during concert discovery with raw scraper data, then asynchronously enriched via MusicBrainz and Google Places to obtain canonical names and external IDs. Neither pipeline currently extracts latitude/longitude, despite both APIs returning coordinates in their responses.

## Goals / Non-Goals

**Goals:**

- Implement proximity-based NEARBY classification using Haversine distance between user home centroid and venue lat/lng
- Consolidate home/nearby/away lane classification in the backend as shared domain logic
- Restructure `ListByFollowerResponse` to return date-grouped, lane-classified concert data
- Enable `HYPE_TYPE_NEARBY` in the notification filter with real proximity logic
- Extract and persist venue coordinates from existing enrichment pipeline responses

**Non-Goals:**

- User-configurable proximity radius (fixed at 200km for Phase 1)
- Real-time GPS-based proximity (uses static home area centroid)
- PostGIS or spatial database extensions (Haversine computed in application layer)
- Support for countries other than Japan in Phase 1 (centroid data is Japan-only)
- Exposing venue lat/lng in the proto Venue entity (backend-internal only for now)

## Decisions

### D1: Haversine distance with venue lat/lng (not admin_area centroid-to-centroid)

Compare the user's home area centroid against the venue's actual latitude/longitude from external place services, rather than comparing centroids of two admin areas.

**Rationale**: Venue-level coordinates are more accurate — a concert hall on the border of two prefectures is classified correctly. Admin-area centroids lose precision for large prefectures (e.g., Hokkaido spans 500km). The enrichment pipeline already calls Google Places and MusicBrainz, which both return coordinates — no additional API calls needed.

**Alternative rejected**: Admin-area centroid-to-centroid comparison. Simpler but less accurate, and fails for venues without admin_area.

### D2: Static Go map for prefecture centroids (not DB table)

Store 47 Japanese prefecture centroid coordinates as a Go `map[string]LatLng` constant in `internal/geo/centroid.go`, keyed by ISO 3166-2 code.

**Rationale**: Phase 1 is Japan-only with a fixed, small dataset. A DB table adds migration, query, and caching complexity for no benefit. Data source: Geospatial Information Authority of Japan (GSI) published prefecture capital coordinates.

**Alternative rejected**: PostgreSQL table with centroid data. Better for multi-country support but premature for Phase 1. Migration path is straightforward when needed.

### D3: Fixed 200km threshold

Use a fixed Haversine distance threshold of 200km for the NEARBY boundary.

**Rationale**: 200km covers reasonable day-trip ranges across Japan — Tokyo captures the entire Kanto region plus Shizuoka/Yamanashi/Nagano (9 prefectures), Osaka captures 13 including Nagoya. For Hokkaido (where no other prefectural capital is within 200km), venue-level coordinates still capture intra-prefecture venues like Asahikawa (130km from Sapporo) and Obihiro (185km).

### D4: Lane classification as backend domain logic

Move the home/nearby/away classification from the frontend `assignLane()` function to a backend domain service (`internal/geo.ClassifyLane`), shared by both the `ListByFollower` RPC handler and `NotifyNewConcerts()`.

**Rationale**: Lane classification is a domain concept, not a presentation concern. The notification filter and dashboard must agree on what "nearby" means. Centralizing in the backend ensures consistency and allows threshold changes without frontend deployment.

**Classification rules**:
1. `venue.admin_area == user.home.level_1` → HOME
2. `venue.latitude/longitude` present AND `Haversine(home_centroid, venue_latlng) <= 200km` → NEARBY
3. Everything else (no coordinates, beyond threshold, no user home) → AWAY

### D5: Restructure ListByFollowerResponse to DateLaneGroup

Replace the flat `repeated Concert concerts` with `repeated DateLaneGroup groups`, where each group contains a date and three lane-specific concert lists.

```protobuf
message ListByFollowerResponse {
  repeated DateLaneGroup groups = 1;
}

message DateLaneGroup {
  entity.v1.LocalDate date = 1;
  repeated entity.v1.Concert home = 2;
  repeated entity.v1.Concert nearby = 3;
  repeated entity.v1.Concert away = 4;
}
```

**Rationale**: The frontend already structures data this way (DateGroup with home/nearby/away arrays). Server-side grouping eliminates redundant processing and the need for the frontend to fetch user home separately. Breaking change is acceptable (no users yet).

### D6: Extract coordinates during enrichment (not discovery)

Venue lat/lng is populated during the enrichment pipeline (MusicBrainz/Google Places resolution), not during initial concert discovery.

**Rationale**: Discovery creates venues with minimal scraper data (name + optional admin_area). The enrichment pipeline already calls external APIs that return coordinates — extracting lat/lng is a minimal addition to the existing data flow. Venues with `enrichment_status = 'pending'` or `'failed'` will have NULL coordinates and fall into the AWAY lane, which is acceptable.

### D7: Venue coordinates are backend-internal (not in proto Venue)

Latitude and longitude are stored in the `venues` DB table and the Go `entity.Venue` struct, but are NOT added to the proto `Venue` message.

**Rationale**: Coordinates are used only for backend proximity calculation. Adding them to proto creates a public API surface that requires versioning discipline. If frontend map features are needed later, a dedicated field can be added then.

## Risks / Trade-offs

- **[Enrichment coverage gap]** Venues with `enrichment_status = 'pending'` or `'failed'` have no lat/lng and always classify as AWAY. This is acceptable because enrichment runs asynchronously after discovery, and failed enrichment indicates the venue couldn't be resolved by any external service. → Mitigation: Monitor enrichment success rate; consider re-running failed venues periodically.

- **[MusicBrainz coordinate availability]** Not all MusicBrainz Place records have coordinates populated. → Mitigation: Fall through to Google Places, which has near-universal coordinate coverage for venue searches.

- **[Breaking RPC change]** `ListByFollowerResponse` restructuring breaks existing frontend. → Mitigation: No users in production; frontend and backend deploy together. Add `buf skip breaking` label to specification PR.

- **[Hokkaido edge case]** 200km from Sapporo covers no other prefectural capital. → Mitigation: Venue-level lat/lng means intra-Hokkaido venues (Asahikawa 130km, Obihiro 185km) are correctly classified as NEARBY. This is the intended behavior.
