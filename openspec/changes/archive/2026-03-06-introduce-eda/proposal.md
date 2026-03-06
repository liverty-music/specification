## Why

The backend's CronJob loop (search → notify → enrich) is tightly coupled: notification delivery is blocked until the entire search loop completes, venue enrichment runs only after all searches finish, and a single artist's external API failure can cascade via the circuit breaker to halt all remaining artists. Introducing Event-Driven Architecture (NATS JetStream + Watermill) decouples these processing stages, adds retry resilience via persistent messaging, and enables independent scaling of consumers.

## What Changes

- Add NATS JetStream as the messaging backbone (3-node HA cluster on GKE)
- Integrate Watermill as the Go-side pub/sub abstraction (GoChannel for local dev, NATS for production)
- Refactor `ConcertUseCase.SearchNewConcerts()` to publish `concert.discovered.v1` event after Gemini API call and deduplication, removing venue resolution and concert persistence from this method
- Introduce event consumers that handle: concert creation (`concert.discovered.v1`), fan notifications (`concert.created.v1`), venue enrichment (`venue.created.v1`)
- Add a new `cmd/consumer/main.go` entry point as a unified Watermill Router process
- **BREAKING**: `SearchNewConcerts` return type changes from `([]*entity.Concert, error)` to `error`
- Deploy KEDA for NATS JetStream lag-based autoscaling of the consumer Deployment
- All events use CloudEvents v1.0 envelope format with JSON payloads

## Capabilities

### New Capabilities
- `event-messaging`: NATS JetStream cluster infrastructure, Watermill publisher/subscriber abstraction, CloudEvents envelope, Watermill Router middleware (retry, logging, error handling)
- `event-consumers`: Consumer handlers for concert discovery pipeline events (concert.discovered, concert.created, venue.created), unified consumer process lifecycle

### Modified Capabilities
- `auto-concert-discovery`: `SearchNewConcerts` becomes a pure "search and publish" function; venue resolution, concert persistence, and notification delivery move to event consumers; CronJob becomes a publish-only loop
- `venue-normalization`: Enrichment triggered by `venue.created.v1` event instead of CronJob post-step

## Impact

- **Backend**: Modified files: `concert_uc.go`, `concert-discovery/main.go`, `di/provider.go`, `di/job.go`, `di/app.go`, `config.go`. New files: `cmd/consumer/main.go`, `di/consumer.go`, messaging infrastructure, event handlers. `go.mod` gains `watermill`, `watermill-nats/v2`, `nats.go` dependencies.
- **Kubernetes**: New `nats` and `keda` namespaces with Helm-based ArgoCD Applications. New consumer Deployment + KEDA ScaledObject in `backend` namespace. NATS_URL config added to server, CronJob, and consumer ConfigMaps.
- **GCP APIs**: No new APIs required (NATS and KEDA are self-hosted on GKE).
- **Frontend**: No changes.
- **Proto (RPC)**: No changes to existing service definitions.
- **Artist Follow**: Out of scope. Follow-related event-driven refactoring (`artist.followed.v1`, resolve-official-site, search-first-concerts) will be handled separately.
