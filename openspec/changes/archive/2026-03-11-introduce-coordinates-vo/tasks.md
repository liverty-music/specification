## 1. Proto Schema (specification repo)

- [x] 1.1 Create `entity/v1/coordinates.proto` with `Coordinates` message (`double latitude`, `double longitude`)
- [x] 1.2 Replace `optional double centroid_latitude` (field 4) and `optional double centroid_longitude` (field 5) on `Home` with `optional Coordinates centroid = 4`, reserve field 5
- [x] 1.3 Update `Home` message comments to reference `Coordinates centroid`
- [x] 1.4 Run `buf lint` and `buf format -w`, verify breaking changes are expected

## 2. Go Entity Layer (backend repo)

- [x] 2.1 Create `entity.Coordinates` struct with `Latitude float64` and `Longitude float64`
- [x] 2.2 Replace `Home.Latitude float64` and `Home.Longitude float64` with `Centroid *Coordinates`
- [x] 2.3 Replace `Venue.Latitude *float64` and `Venue.Longitude *float64` with `Coordinates *Coordinates`
- [x] 2.4 Replace `VenuePlace.Latitude *float64` and `VenuePlace.Longitude *float64` with `Coordinates *Coordinates`
- [x] 2.5 Update `Concert.ProximityTo` to use `home.Centroid` and `venue.Coordinates`
- [x] 2.6 Update `Concert.ProximityTo` unit tests

## 3. Infrastructure Layer (backend repo)

- [x] 3.1 Rename `infrastructure/geo.LatLng` struct to `Coordinates`
- [x] 3.2 Update `user_repo.go` to map between DB columns and `*entity.Coordinates` for Home centroid
- [x] 3.3 Update `venue_repo.go` to map between DB columns and `*entity.Coordinates` for Venue coordinates
- [x] 3.4 Update `concert_repo.go` to map between DB columns and `*entity.Coordinates` for Venue coordinates
- [x] 3.5 Update MusicBrainz `place_searcher.go` to return `*entity.Coordinates` in `VenuePlace`
- [x] 3.6 Update Google Maps `place_searcher.go` to return `*entity.Coordinates` in `VenuePlace`

## 4. UseCase Layer (backend repo)

- [x] 4.1 Update `venue_enrichment_uc.go` to use `Venue.Coordinates` and `VenuePlace.Coordinates`

## 5. Adapter Layer (backend repo)

- [x] 5.1 Update RPC mapper for `Home.centroid` proto-to-entity conversion

## 6. Tests and Verification (backend repo)

- [x] 6.1 Update infrastructure tests (`client_test.go`, `venue_repo` tests) for `*Coordinates`
- [x] 6.2 Update usecase tests referencing venue/home coordinate fields
- [x] 6.3 Run `go build ./...` to verify compilation
- [x] 6.4 Run `go test ./...` to verify all tests pass

## 7. New Coordinates Test Coverage (backend repo)

- [x] 7.1 Add `geo/centroid_test.go`: test `ResolveCentroid` for known JP code (returns coords, ok=true) and unsupported code (ok=false)
- [x] 7.2 Add `venue_repo_test.go` test: `UpdateEnriched` with non-nil Coordinates → `Get` returns same coords; with nil Coordinates → `Get` returns nil coords
- [x] 7.3 Add `user_repo_test.go` test: Create/UpdateHome with supported JP code → `Get` returns non-nil `Home.Centroid`; unsupported code → nil `Centroid`
- [x] 7.4 Add `concert_repo_test.go` assertion: `ListByFollower` result includes `Venue.Coordinates` when DB has lat/lng, nil when DB has NULLs
- [x] 7.5 Add `maps/google/place_searcher_test.go`: test `SearchPlace` returns non-nil Coordinates when response has lat/lng, nil when absent
- [x] 7.6 Add `music/musicbrainz/place_searcher_test.go`: test `SearchPlace` returns non-nil Coordinates when response has lat/lng, nil when absent
- [x] 7.7 Add `venue_enrichment_uc_test.go` assertion: verify `UpdateEnriched` is called with correct `Coordinates` value from PlaceSearcher response
- [x] 7.8 Run `go test ./...` to verify all new tests pass
