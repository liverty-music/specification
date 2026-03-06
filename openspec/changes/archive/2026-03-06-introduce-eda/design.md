## Context

The Liverty Music backend is a single Go module with two entry points (`cmd/api`, `cmd/job/concert-discovery`). The CronJob runs a synchronous loop: for each followed artist, it calls `SearchNewConcerts` (Gemini API), then `NotifyNewConcerts` (Web Push fan-out), and finally `EnrichPendingVenues` (MusicBrainz + Google Maps) as a post-step. These stages are tightly coupled — notification is blocked until search completes for all artists, and a single artist's failure cascades via the circuit breaker.

The system runs on GKE Autopilot with ArgoCD GitOps. Helm-based infrastructure components (ESO, Reloader, Atlas Operator) each have dedicated namespaces with base/overlay Kustomize structure.

## Goals / Non-Goals

**Goals:**
- Decouple concert persistence, notification, and venue enrichment from the CronJob search loop
- Add retry resilience to concert creation, notification, and venue enrichment via persistent messaging
- Enable independent scaling of consumer workloads
- Maintain Gemini API throttling (CronJob sequential loop preserved)
- Use CloudEvents v1.0 as the event envelope standard

**Non-Goals:**
- Artist Follow event-driven refactoring (`artist.followed.v1`) — handled separately
- GCS cold archive — deferred
- Transactional Outbox pattern (uses publish-after-commit)
- Microservice decomposition (the system remains a single Go module)
- Event sourcing or CQRS
- Proto definitions for event schemas (Go structs + JSON sufficient for single-module system)

## Decisions

### 1. Messaging: NATS JetStream + Watermill

**Choice**: NATS JetStream as the message broker, Watermill as the Go abstraction.

**Why NATS over alternatives**:
- Lightweight, single-binary deployment on K8s (vs Kafka's ZooKeeper/KRaft complexity)
- JetStream provides at-least-once delivery with consumer ack, replay, and persistence
- Native K8s Helm chart with straightforward HA configuration
- KEDA has a first-class NATS JetStream scaler

**Why Watermill**:
- `Publisher`/`Subscriber` interfaces abstract away NATS-specific APIs
- `GoChannel` adapter for local development without running NATS
- Built-in Router with middleware (retry, logging, error handling, poison queue)
- The specification requires vendor lock-in avoidance

**Alternatives considered**:
- Google Cloud Pub/Sub: managed but adds GCP dependency, higher latency for in-cluster communication, cost per message
- Redis Streams: simpler but weaker durability guarantees, no built-in consumer groups with ack

### 2. Stream Topology: Single Stream

**Choice**: One JetStream stream `LIVERTY_MUSIC` with subject filter `liverty-music.>`.

**Why**: 3 event types and 3 consumers do not justify multi-stream complexity. All events share the same retention policy (7-day max age). GCS archiver (future) subscribes to one stream.

**When to split**: If event types need different retention, replication, or storage policies.

### 3. Event Type Naming: CloudEvents + Domain Past Tense

**Choice**: `liverty-music.<aggregate>.<past-tense-verb>.v1`

Events in this change:
- `liverty-music.concert.discovered.v1`
- `liverty-music.concert.created.v1`
- `liverty-music.venue.created.v1`

### 4. Event Granularity: Artist-Level Batch for concert.discovered

**Choice**: `concert.discovered.v1` carries the full batch of scraped concerts for one artist (post-deduplication).

**Why**: Downstream `notify-fans` consumer sends one notification per artist ("N new concerts found"), not per concert. Publishing per-concert would require aggregation logic in the consumer, violating the existing notification semantics.

### 5. Publish Strategy: Publish After Commit

**Choice**: Uses publish-after-commit (no Outbox pattern).

**Why**: If publish fails, the consequence is a missed notification or missed venue enrichment — recoverable by the next CronJob run. The Outbox pattern adds significant complexity (polling, deduplication) that is not justified for current reliability requirements.

### 6. UseCase → Publisher Dependency: Watermill `message.Publisher` directly

**Choice**: UseCases depend on Watermill's `message.Publisher` interface, not a custom `EventPublisher`.

**Why**: Watermill's `Publisher` is already an interface (`Publish(topic string, messages ...*message.Message) error`). Wrapping it in another interface adds indirection without benefit in a single-module system. Tests use Watermill's built-in `GoChannel` publisher.

### 7. Consumer Process: Single Unified `cmd/consumer/main.go`

**Choice**: One consumer binary with all handlers registered on a single Watermill Router.

**Why**: 3 handlers do not justify separate Deployments. The system is a monolith — the API server already handles all RPCs in one process. A single consumer matches this philosophy.

**When to split**: If a specific handler becomes resource-intensive enough to warrant independent scaling.

### 8. Local Development: GoChannel Only

**Choice**: Local dev uses Watermill's `GoChannel` adapter (with `FanOut: true`). No local NATS.

**Why**: Reduces local setup complexity. GoChannel supports fan-out to multiple handlers. JetStream-specific behavior (ack timeout, redelivery, replay) is tested in CI with a NATS container.

### 9. SearchNewConcerts Publishes Internally

**Choice**: `SearchNewConcerts()` calls `publisher.Publish()` inside the method body, not externally by the caller.

**Why**: `SearchNewConcerts` is called from multiple paths (CronJob loop, and potentially future callers). Publishing inside the method ensures every call path emits the event without caller coordination.

### 10. Kubernetes Namespace Strategy: Dedicated Namespaces for NATS and KEDA

**Choice**: `nats` and `keda` namespaces, following the existing convention where each Helm-based infra component gets its own namespace (like `external-secrets`, `reloader`, `atlas-operator`).

### 11. Worker Identity: Reuse `backend-app` GCP SA Initially

**Choice**: The consumer Deployment reuses the existing `backend-app` GCP service account via Workload Identity.

**Why**: The consumer needs the same permissions as the API server (Cloud SQL access, logging, monitoring). Creating a separate SA adds operational overhead without security benefit since the consumer runs the same codebase. Separate SA can be introduced when permissions diverge.

## Risks / Trade-offs

**[Publish-after-commit message loss]** → If the process crashes between DB commit and NATS publish, the event is lost. Mitigation: CronJob runs daily and re-discovers concerts. Venue enrichment batch can be run manually as safety net.

**[GoChannel divergence from NATS]** → GoChannel does not replicate JetStream ack/nack/retry semantics. Mitigation: CI runs integration tests with a NATS container. Unit tests verify handler logic independent of transport.

**[NATS cluster failure]** → If all 3 NATS nodes are down, `publisher.Publish()` fails and the event never enters JetStream — NATS cannot redeliver what was never published. Mitigation: CronJob logs publish errors and continues its loop for remaining artists. Because the search log is written before publishing (publish-after-commit), the failed artist is marked as searched and won't be re-searched until the 24-hour search log TTL expires. Recovery path: after the TTL expires, the next CronJob run re-discovers and re-publishes the concerts.

**[Consumer backpressure]** → If consumers fall behind, NATS JetStream buffers messages (7-day retention). KEDA scales consumer pods based on lag. Risk is disk exhaustion on NATS PVCs. Mitigation: Monitor `jetstream_consumer_num_pending` metric, set alerts.

## Migration Plan

1. **Infrastructure first**: Deploy NATS cluster and KEDA via ArgoCD (no application changes yet)
2. **Consumer deployment**: Deploy consumer process with all handlers (no events flowing yet)
3. **Enable publishing in ConcertUseCase**: `SearchNewConcerts` starts publishing `concert.discovered.v1`. Consumer creates concerts, publishes `concert.created.v1` and `venue.created.v1`. Remove venue/concert creation from `SearchNewConcerts`. CronJob removes `NotifyNewConcerts` and `EnrichPendingVenues` direct calls.
4. **Verify and monitor**: Confirm events flow end-to-end, notifications are delivered, venues are enriched.

Rollback: Revert to previous backend image. NATS cluster can remain running. No data migration needed.
