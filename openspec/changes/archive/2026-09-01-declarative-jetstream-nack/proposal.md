## Why

JetStream streams and consumers are managed **imperatively** today: the backend
creates streams in code at startup (`streams.go`) and runs a homegrown
`ReconcileConsumers` that walks **every** stream and **deletes any durable not in
the calling app's desired set**. That design silently assumes **one always-on
consumer app owns all durables**. The organizer media pipeline broke that
assumption by adding a **second** consumer (media-processor) with a *partial*
desired set, which makes the two apps' reconciles **mutually delete each other's
durables** (event-consumer would wipe `media_uploaded`; media-processor would
wipe all 18 event-consumer durables — a latent, prod-wide outage, currently
dormant only because a ConfigMap bug prevents media-processor from starting). The
same imperative model also blocks **scale-to-zero**: a durable created by its
worker vanishes when the worker scales to 0, so KEDA has no consumer to measure
and can never wake it.

Migrate JetStream resource management to **declarative NACK CRDs** — the official
NATS Kubernetes approach — which decouples stream/consumer lifecycle from
workloads, eliminating both problems at the root and unblocking a clean,
hack-free scale-to-zero media consumer.

## What Changes

- **BREAKING (management model)** Adopt **NACK** (`nats/nack` Helm chart,
  control-loop mode) as the **sole, exclusive** manager of JetStream streams and
  consumers. NACK enforces state and forbids external mutation, so app-side
  management must be fully removed for migrated resources.
- Declare all **Streams** (11: CONCERT, VENUE, ARTIST, USER, NOTIFICATION,
  SALES_PHASE, TICKET_JOURNEY, TICKET_EMAIL, ORGANIZER, MEDIA, POISON) and
  **Consumers** (~19 behavior-named durables + `media_uploaded`) as
  `jetstream.nats.io/v1beta2` CRDs (GitOps/ArgoCD-managed), matching the current
  live config exactly so adoption is a no-op.
- **Backend**: remove imperative stream creation (`streams.go`) and the homegrown
  `ReconcileConsumers`; change subscribers to **bind to** the NACK-managed
  durables instead of creating them.
- **media-processor → `media-consumer`** (rename for consistency with
  `event-consumer`): convert from the misused **ScaledJob** to a long-running
  **Deployment + KEDA `ScaledObject` `minReplicaCount: 0`** bound to a
  declarative `media_uploaded` Consumer — a proper, hack-free scale-to-zero
  consumer (idle ≈ $0; the NACK-managed durable persists while at 0 replicas).
- **Staged, reversible cut-over** with a mandatory dev dry-run proving NACK
  adopts live durables as a **no-op** (no cursor reset, no deliver-group churn),
  to avoid a stale-durable wedge outage.

## Capabilities

### New Capabilities
<!-- None. This refines how the existing JetStream reliability capability is
     realized (declarative vs imperative) and adds scale-to-zero. -->

### Modified Capabilities
- `jetstream-consumer-reliability`: the requirement that durable configuration is
  **reconciled by the app on startup** changes to **declaratively managed by an
  in-cluster controller (NACK)** that exclusively owns streams/consumers; add that
  a consumer MAY scale to zero (its durable persists independent of the workload)
  and that per-app global reconcile no longer deletes other consumers' durables.

## Impact

- **cloud-provisioning**: new `nats/nack` Helm release (controller,
  control-loop); `Stream` ×11 + `Consumer` ×19 CRDs (GitOps); `media-consumer`
  `Deployment` + `ScaledObject` (min=0) replacing the ScaledJob; rename of the
  media workload/image/GSA/WI/config/monitoring/bump-prod-pin entries from
  `media-processor` to `media-consumer`.
- **backend**: remove `streams.go` stream creation and `ReconcileConsumers`;
  subscribers become bind-only; rename `cmd/job/media-processor` →
  `cmd/consumer/media-consumer` (long-running) + DI/config rename; no proto, no
  BSR release.
- **Risk**: live prod durable adoption must match current config exactly (else
  NACK recreates durables → 2026-07-class stale-durable delivery outage); touches
  every prod event flow (push, discovery, analytics, ticketing, organizer) →
  staged cut-over + per-stage rollback, dev-proven first.
- **Non-Goals**: migrating KV/ObjectStore to NACK; changing event schemas or
  subjects; the media upload/attach RPC surface (already shipped in
  `organizer-media-pipeline`).
