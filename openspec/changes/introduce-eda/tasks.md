## 1. Infrastructure: NATS JetStream on GKE

- [x] 1.1 Create `nats` namespace in `k8s/init/namespaces.yaml`
- [x] 1.2 Create `k8s/namespaces/nats/base/` with Helm chart kustomization and values (3-node HA, JetStream, `premium-rwo` PVC)
- [x] 1.3 Create `k8s/namespaces/nats/overlays/dev/` with dev-specific overrides
- [x] 1.4 Create ArgoCD Application `k8s/argocd-apps/dev/nats.yaml`
- [ ] 1.5 Deploy and verify NATS cluster is running (`kubectl get pods -n nats`)

## 2. Infrastructure: KEDA

- [x] 2.1 Create `keda` namespace in `k8s/init/namespaces.yaml`
- [x] 2.2 Create `k8s/namespaces/keda/base/` with Helm chart kustomization and values
- [x] 2.3 Create `k8s/namespaces/keda/overlays/dev/` with dev-specific overrides
- [x] 2.4 Create ArgoCD Application `k8s/argocd-apps/dev/keda.yaml`
- [ ] 2.5 Deploy and verify KEDA controller is running (`kubectl get pods -n keda`)

## 3. Backend: Watermill Messaging Foundation

- [x] 3.1 Add `watermill`, `watermill-nats/v2`, `nats.go` to `go.mod`
- [x] 3.2 Add `NATSConfig` struct to `pkg/config/config.go` (`NATS_URL`, `NATS_STREAM_NAME`)
- [x] 3.3 Create `internal/infrastructure/messaging/publisher.go` — Watermill Publisher initialization (NATS or GoChannel based on config)
- [x] 3.4 Create `internal/infrastructure/messaging/subscriber.go` — Watermill Subscriber initialization
- [x] 3.5 Create `internal/infrastructure/messaging/router.go` — Watermill Router with middleware (retry, poison queue, logging, OTel)
- [x] 3.6 Create `internal/infrastructure/messaging/cloudevents.go` — CloudEvents metadata helper for Watermill messages
- [x] 3.7 Define event data structs (`ConcertDiscoveredEvent`, `ConcertCreatedEvent`, `VenueCreatedEvent`)

## 4. Backend: Refactor SearchNewConcerts to Search-and-Publish

- [x] 4.1 Add `message.Publisher` dependency to `concertUseCase` struct and `NewConcertUseCase` constructor
- [x] 4.2 Change `SearchNewConcerts` return type from `([]*entity.Concert, error)` to `error`
- [x] 4.3 Remove venue resolution logic (lines 198-234) from `SearchNewConcerts`
- [x] 4.4 Remove concert entity assembly and `concertRepo.Create` bulk insert (lines 236-260) from `SearchNewConcerts`
- [x] 4.5 Add deduplication check + `concert.discovered.v1` publish (artist-level batch) after Gemini API call
- [x] 4.6 Update `ConcertUseCase` interface to reflect new `SearchNewConcerts` signature
- [x] 4.7 Update DI in `internal/di/provider.go` and `internal/di/job.go` to inject Publisher into `concertUseCase`
- [x] 4.8 Update tests for `SearchNewConcerts`
- [x] 4.9 Remove `concerts` field from `SearchNewConcertsResponse` proto (response is now empty)
- [x] 4.10 Update `SearchNewConcerts` RPC doc comment to describe async event-driven behavior

## 5. Backend: Consumer Process and Handlers

- [x] 5.1 Create `cmd/consumer/main.go` — entry point with Watermill Router, signal handling, graceful shutdown
- [x] 5.2 Create `internal/di/consumer.go` — `ConsumerApp` struct and `InitializeConsumerApp` with all handler dependencies
- [x] 5.3 Create `internal/adapter/event/concert_handler.go` — `create-concerts` handler (venue resolution, concert INSERT, publish `concert.created.v1` and `venue.created.v1`)
- [x] 5.4 Create `internal/adapter/event/notification_handler.go` — `notify-fans` handler (calls `PushNotificationUseCase.NotifyNewConcerts`)
- [x] 5.5 Create `internal/adapter/event/venue_handler.go` — `enrich-venue` handler (calls venue enrichment logic per venue)
- [x] 5.6 Add public `EnrichOne(ctx, venueID)` method to `VenueEnrichmentUseCase` interface and implementation
- [x] 5.7 Write unit tests for each handler

## 6. Backend: CronJob Simplification

- [x] 6.1 Remove `NotifyNewConcerts` call from CronJob loop in `cmd/job/concert-discovery/main.go`
- [x] 6.2 Remove `EnrichPendingVenues` call from CronJob post-step
- [x] 6.3 Remove `PushNotificationUC` and `VenueEnrichUC` from `JobApp` struct and `InitializeJobApp`
- [x] 6.4 Update CronJob to handle new `SearchNewConcerts` return type (error only, no `[]Concert`)
- [x] 6.5 Update CronJob logging (remove `totalDiscovered` count since it's no longer returned)

## 7. Kubernetes: Consumer Deployment

- [x] 7.1 Create `k8s/namespaces/backend/base/worker/consumer/kustomization.yaml`
- [x] 7.2 Create `k8s/namespaces/backend/base/worker/consumer/deployment.yaml` — consumer Deployment with health probes
- [x] 7.3 Create `k8s/namespaces/backend/base/worker/consumer/configmap.env` — NATS_URL and other env vars
- [x] 7.4 Create KEDA `ScaledObject` for consumer Deployment in `k8s/namespaces/backend/base/worker/consumer/scaledobject.yaml`
- [x] 7.5 Add `worker/consumer` to `k8s/namespaces/backend/base/kustomization.yaml` resources
- [x] 7.6 Add `NATS_URL` to `k8s/namespaces/backend/base/server/configmap.env`
- [x] 7.7 Add `NATS_URL` to `k8s/namespaces/backend/base/cronjob/concert-discovery/configmap.env`
- [x] 7.8 Update `k8s/namespaces/backend/overlays/dev/kustomization.yaml` for consumer overlay

## 8. API Server: Watermill Publisher Integration

- [x] 8.1 Add Watermill Publisher initialization to `internal/di/provider.go`
- [x] 8.2 Add NATS Publisher to `App` closers in `internal/di/app.go`
- [x] 8.3 Add `NATS_URL` to API server config validation (optional in local, required in prod)

## 9. End-to-End Verification

- [ ] 9.1 Verify: CronJob runs → `SearchNewConcerts` publishes `concert.discovered.v1` → concerts created → notifications sent → venues enriched
- [ ] 9.2 Verify: KEDA scales consumer pods based on NATS JetStream lag
- [ ] 9.3 Verify: GoChannel adapter works for local development (all handlers receive events with FanOut)
- [ ] 9.4 Monitor NATS JetStream metrics (pending messages, ack rates) in production
