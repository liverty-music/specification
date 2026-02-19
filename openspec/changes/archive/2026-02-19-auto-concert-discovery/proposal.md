## Why

Users currently only discover new concerts when they manually search for an artist. This means fans miss new concert announcements unless they actively check the app. By automating concert discovery for followed artists via a daily scheduled job, the platform proactively surfaces new live events — increasing engagement and delivering on the core value proposition of a "personalized concert notification platform."

## What Changes

- Add a K8s CronJob that runs daily at 18:00 JST, iterating over all followed artists and calling the existing `SearchNewConcerts` use case to discover and persist new concerts.
- Add `ListAllFollowed` method to `ArtistRepository` to retrieve distinct artists followed by any user.
- Change `ConcertRepository.Create` signature from single entity to variadic (`...*Concert`) for bulk insert support.
- Wrap bare error returns in `SearchNewConcerts` with `fmt.Errorf` context for observability.
- Add a lightweight DI initializer (`InitializeJobApp`) for batch job entry points that don't require an HTTP server.
- Add K8s CronJob manifests with Kustomize overlays (dev: weekly on Fridays, prod/staging: daily).

## Capabilities

### New Capabilities
- `auto-concert-discovery`: Scheduled batch job that discovers new concerts for all followed artists, including the CronJob entry point, job-specific DI, and K8s manifests.

### Modified Capabilities
- `concert-service`: `ConcertRepository.Create` changes from `Create(ctx, *Concert)` to `Create(ctx, ...*Concert)` for bulk insert. Error wrapping added to `SearchNewConcerts`.
- `artist-following`: New `ListAllFollowed(ctx) ([]*Artist, error)` method on `ArtistRepository` to list distinct artists followed across all users.

## Impact

- **Backend code**: `internal/entity/artist.go`, `internal/entity/concert.go`, `internal/infrastructure/database/rdb/artist_repo.go`, `internal/infrastructure/database/rdb/concert_repo.go`, `internal/usecase/concert_uc.go`, new `internal/di/job.go`, new `cmd/job/concert-discovery/main.go`.
- **Infrastructure**: New K8s CronJob manifests in `cloud-provisioning/k8s/namespaces/backend/base/cronjob/concert-discovery/` with dev overlay for reduced schedule.
- **Docker**: Dockerfile update to build the new `concert-discovery` binary.
- **No API changes**: No new RPC endpoints or proto changes. The CronJob reuses existing internal use cases.
