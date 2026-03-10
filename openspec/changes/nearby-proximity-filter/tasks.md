## 1. Proto Schema Changes (specification repo)

- [x] 1.1 Add `DateLaneGroup` message to `concert_service.proto` with `date`, `home`, `nearby`, `away` fields
- [x] 1.2 Restructure `ListByFollowerResponse` to use `repeated DateLaneGroup groups` (replacing `repeated Concert concerts`)
- [x] 1.3 Run `buf lint` and `buf format -w` to validate proto changes

## 2. Venue Coordinates (backend repo)

- [x] 2.1 Add `latitude` and `longitude` columns (`DOUBLE PRECISION`, nullable) to `venues` table in `schema.sql`
- [ ] 2.2 Generate Atlas migration with `atlas migrate diff --env local add_venue_coordinates`
- [x] 2.3 Add `Latitude *float64` and `Longitude *float64` fields to `entity.Venue` struct
- [x] 2.4 Update `VenueEnrichmentRepository.UpdateEnriched` to persist latitude/longitude
- [ ] 2.5 Update venue repository queries (`ListByFollower` JOIN) to include latitude/longitude

## 3. Enrichment Pipeline Coordinate Extraction (backend repo)

- [x] 3.1 Extend MusicBrainz `placeSearchResponse` struct to parse `coordinates.latitude` and `coordinates.longitude`
- [x] 3.2 Add `Latitude` and `Longitude` fields to MusicBrainz `Place` struct
- [x] 3.3 Extend Google Places `textSearchResponse` struct to parse `geometry.location.lat` and `geometry.location.lng`
- [x] 3.4 Add `Latitude` and `Longitude` fields to Google Places `Place` struct
- [x] 3.5 Add `Latitude` and `Longitude` fields to `entity.VenuePlace`
- [x] 3.6 Update `PlaceSearcher` adapters (MusicBrainz and Google) to pass coordinates through to `VenuePlace`
- [x] 3.7 Update `venueEnrichmentUseCase.enrichOne` to set coordinates on the enriched venue entity
- [ ] 3.8 Write unit tests for coordinate extraction from both MusicBrainz and Google Places responses

## 4. Proximity Classifier (backend repo)

- [x] 4.1 Create `internal/geo/centroid.go` with `PrefectureCentroid` map (47 JP prefectures, sourced from GSI)
- [x] 4.2 Create `internal/geo/haversine.go` with `Haversine(lat1, lng1, lat2, lng2) float64` function
- [x] 4.3 Create `internal/geo/lane.go` with `ClassifyLane(homeLevel1 string, venueLat, venueLng *float64, venueAdminArea *string) Lane` function
- [x] 4.4 Define `Lane` type (`HOME`, `NEARBY`, `AWAY`) in `internal/geo/lane.go`
- [x] 4.5 Write unit tests for Haversine calculation (known distances: Tokyo-Saitama, Tokyo-Osaka)
- [x] 4.6 Write unit tests for ClassifyLane (HOME match, NEARBY within threshold, AWAY beyond threshold, missing coordinates, missing home)

## 5. ListByFollower Restructure (backend repo)

- [x] 5.1 Update `ConcertRepository.ListByFollower` query to JOIN venue lat/lng and return venue coordinates
- [x] 5.2 Create `ConcertUseCase.ListByFollowerGrouped` method that fetches user home, classifies concerts into lanes, and groups by date
- [ ] 5.3 Update `ConcertHandler.ListByFollower` to call the grouped usecase method and map to `DateLaneGroup` proto response (blocked: BSR gen)
- [ ] 5.4 Update RPC handler mapper to convert domain lane groups to proto `DateLaneGroup` messages (blocked: BSR gen)
- [x] 5.5 Write unit tests for the grouped usecase method

## 6. Notification Filter Update (backend repo)

- [x] 6.1 Update `NotifyNewConcerts()` NEARBY case to use `geo.ClassifyLane` instead of ANYWHERE fallback
- [x] 6.2 Add `ListFollowersWithHype` to return user home area alongside hype level (if not already included)
- [x] 6.3 Write unit tests for NEARBY notification filtering (within 200km: notify, beyond 200km: skip)

## 7. Frontend Adaptation (frontend repo)

- [ ] 7.1 Update `concert-service.ts` to parse new `DateLaneGroup[]` response structure
- [ ] 7.2 Simplify `dashboard-service.ts`: remove `assignLane()`, `fetchUserHome()`, and manual grouping logic
- [ ] 7.3 Map server `DateLaneGroup` directly to `DateGroup` type used by `live-highway` component
- [ ] 7.4 Update hype selector to show 4 options (WATCH / HOME / NEARBY / ANYWHERE) instead of 3
- [ ] 7.5 Remove `HYPE_TYPE_NEARBY` rejection in `SetHype` RPC validation (specification + backend)
- [ ] 7.6 Update frontend unit tests for dashboard service and hype selector
