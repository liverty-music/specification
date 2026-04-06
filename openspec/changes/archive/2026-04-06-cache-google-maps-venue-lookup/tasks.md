## 1. Database Migration

- [x] 1.1 Add Atlas migration: create unique index `idx_venues_listed_name_admin_area` on `venues(listed_venue_name, admin_area)`
- [x] 1.2 Register the new migration file in `k8s/atlas/base/kustomization.yaml`

## 2. Repository Layer

- [x] 2.1 Add `GetByListedName(ctx context.Context, listedVenueName string, adminArea *string) (*Venue, error)` to the `VenueRepository` interface in `internal/entity/venue.go`
- [x] 2.2 Implement `GetByListedName` in `internal/infrastructure/database/rdb/venue_repo.go` using an exact match on `(listed_venue_name, admin_area)`
- [x] 2.3 Add integration test for `GetByListedName` in `internal/infrastructure/database/rdb/venue_repo_test.go` covering: found, not found, and NULL admin_area cases
- [x] 2.4 Regenerate mocks: run `mockery` to update `internal/entity/mocks/mock_VenueRepository.go`

## 3. UseCase Layer

- [x] 3.1 Update `resolveVenue()` in `internal/usecase/concert_creation_uc.go` to call `venueRepo.GetByListedName` before invoking the Places API; return immediately on hit
- [x] 3.2 Update the batch-local `newVenues` map key from `place.ExternalID` to `listed_venue_name` so the pre-check and batch cache use the same key
- [x] 3.3 Add unit tests for `resolveVenue` covering: DB hit (API not called), DB miss → API hit → new venue, DB miss → API NotFound (skip)
