## 1. Entity and Repository Changes

- [x] 1.1 Add `ListAllFollowed(ctx context.Context) ([]*Artist, error)` to `ArtistRepository` interface in `internal/entity/artist.go`
- [x] 1.2 Implement `ListAllFollowed` in `internal/infrastructure/database/rdb/artist_repo.go` with `SELECT DISTINCT ... JOIN followed_artists` query
- [x] 1.3 Change `ConcertRepository.Create` signature from `Create(ctx context.Context, concert *Concert) error` to `Create(ctx context.Context, concerts ...*Concert) error` in `internal/entity/concert.go`
- [x] 1.4 Implement bulk INSERT in `internal/infrastructure/database/rdb/concert_repo.go` for the variadic `Create` method

## 2. UseCase Refactoring

- [x] 2.1 Wrap bare error returns in `SearchNewConcerts` with `fmt.Errorf("failed to <operation>: %w", err)` for: get search log, get artist, get official site, list existing concerts, search external API
- [x] 2.2 Refactor `SearchNewConcerts` to collect discovered concerts first, then call `concertRepo.Create(ctx, discovered...)` as a single bulk insert at the end of the loop

## 3. Job DI and Entry Point

- [x] 3.1 Create `internal/di/job.go` with `JobApp` struct and `InitializeJobApp(ctx) (*JobApp, error)` that initializes only config, logger, DB, repos, Gemini searcher, and ConcertUseCase
- [x] 3.2 Create `cmd/job/concert-discovery/main.go` with: `ListAllFollowed` loop, `SearchNewConcerts` per artist, 3-consecutive-error circuit breaker, always exit 0

## 4. K8s Manifests

- [x] 4.1 Create `k8s/namespaces/backend/base/cronjob/concert-discovery/cronjob.yaml` with schedule `0 9 * * *`, `concurrencyPolicy: Forbid`, and resource limits
- [x] 4.2 Create `k8s/namespaces/backend/base/cronjob/concert-discovery/kustomization.yaml` with image reference and configMapGenerator
- [x] 4.3 Update `k8s/namespaces/backend/base/kustomization.yaml` to include `cronjob/concert-discovery` resource
- [x] 4.4 Create dev overlay patch at `k8s/namespaces/backend/overlays/dev/cronjob/concert-discovery/` to override schedule to `0 9 * * 5` (Fridays only)
- [x] 4.5 Update `k8s/namespaces/backend/overlays/dev/kustomization.yaml` to include the schedule patch

## 5. Docker

- [x] 5.1 Update Dockerfile to build `cmd/job/concert-discovery/main.go` as a separate binary target
