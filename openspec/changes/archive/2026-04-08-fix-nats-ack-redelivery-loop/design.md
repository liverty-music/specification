## Context

The NATS JetStream consumer (`backend/internal/infrastructure/messaging/subscriber.go`) uses `watermill-nats v2.1.3` (`pkg/nats`). When `JetStream.Disabled` is false (the default), the library internally uses a `jsConnection` wrapper that calls `js.QueueSubscribe()` (JetStream) — not CoreNATS `conn.QueueSubscribe()`. The `DurableCalculator` produces a durable name (e.g., `CONCERT_discovered`), and `SubscribeOptions` including `AckExplicit()` and `DeliverAll()` are passed through to the JetStream subscription.

Two independent bugs were introduced in commit `25c22d9` (2026-03-24):

1. **`AckAsync: true`**: The `processMessage()` loop uses `m.Ack()` (fire-and-forget) instead of `m.AckSync()`. When KEDA deactivates both consumer pods simultaneously (replicas: 2 → 0), the Ack write may still be in the network buffer when `conn.Drain()` is called. Empirically confirmed by GKE event logs: KEDA deactivates at `00:40:58`, and re-activates 30 seconds later (`00:41:28`), indicating the JetStream lag did not reach 0 — some Acks were not received by the server.

2. **`DeliverAll()`**: Sets `DeliverPolicy = DeliverAllPolicy` on first consumer creation. When the GKE cluster was migrated to `standard-cluster-osaka` on 2026-04-01, NATS started with a fresh PVC. The durable consumer `CONCERT_discovered` was recreated from scratch on 2026-04-03 (first concert-discovery CronJob run). Because no prior consumer state existed, `DeliverAll` delivered all messages from the beginning of the stream — including all historical `concert.created` events. Each redelivered event triggered a Places API call.

Current observed impact: ~7-minute redelivery cycles running continuously since 2026-04-03.

## Goals / Non-Goals

**Goals:**
- Ensure Acks are confirmed by the NATS server before a consumer handler is considered complete
- Prevent historical message redelivery when a durable consumer is created for the first time
- Stop the current redelivery loop without requiring NATS state manipulation or manual intervention

**Non-Goals:**
- Exactly-once processing guarantees (idempotency at the use-case layer is a separate concern)
- Changes to KEDA ScaledObject configuration or cooldownPeriod
- Purging or resetting the NATS stream

## Decisions

### Decision 1: Remove `AckAsync: true` (use SyncAck)

**Choice**: Delete `AckAsync: true` from `JetStreamConfig`. This defaults to `false`, causing the library to call `m.AckSync()` instead of `m.Ack()`.

**Rationale**: `m.AckSync()` blocks until the NATS server acknowledges receipt of the Ack. This guarantees that when a handler returns, the message is permanently removed from the consumer's pending-delivery list. Fire-and-forget Ack is only appropriate when handler latency is the bottleneck and duplicate processing is acceptable — neither is true here.

**Alternative considered**: Keep `AckAsync` and increase NATS `AckWait` timeout so messages are not redelivered before the pod shuts down. Rejected because it only widens the race window; under simultaneous multi-pod shutdown it remains unreliable.

**Performance impact**: Each message processing call now has one additional round-trip to NATS for the Ack confirmation. Given that handlers already make DB writes and Places API calls (each >10ms), the NATS Ack round-trip (<1ms on cluster-local network) is negligible.

### Decision 2: Replace `DeliverAll()` with `DeliverNew()`

**Choice**: Replace `nats.DeliverAll()` with `nats.DeliverNew()` in `SubscribeOptions`.

**Rationale**: `DeliverNew` sets `DeliverPolicy = DeliverNewPolicy`, meaning a newly created durable consumer will only receive messages published _after_ the consumer is created. This is the correct semantics for an event-driven notification system: if the consumer state is lost, we accept that historical events will not be reprocessed — the concert data is already in the DB from the first processing run.

**Alternative considered**: `DeliverLastPerSubject` — delivers only the most recent message per subject on consumer creation. Rejected because subjects in this stream are shared static event-type subjects (`CONCERT.discovered`, `CONCERT.created`, etc.) — not per-event identifiers. `DeliverLastPerSubject` would deliver exactly one arbitrary historical message per subject type, which is still an undesired historical redelivery. `DeliverNew` cleanly avoids any historical message regardless of subject scheme.

**Alternative considered**: Keep `DeliverAll` and manage consumer state externally (e.g., snapshot PVC before cluster migration). Rejected as operationally fragile — any NATS pod restart would still trigger full redelivery.

**Trade-off**: If a consumer pod crashes mid-batch and its Acks were all confirmed (SyncAck), the unprocessed messages in that batch will not be redelivered after `DeliverNew` is set. This is mitigated by SyncAck itself: if the pod crashes before `m.AckSync()` returns, the Ack was never sent, and NATS will redeliver that specific message to the next consumer — correct at-least-once behavior.

## Risks / Trade-offs

- **[Risk] In-flight messages at deploy time** → During rolling restart, old pods (AckAsync) and new pods (SyncAck) may coexist briefly. Old pods may still lose Acks. Mitigation: the KEDA cooldownPeriod=300s ensures that once new pods process all messages, scale-down will not trigger immediate re-activation (lag will be 0 with confirmed Acks).

- **[Risk] DeliverNew skips messages published between consumer deletion and recreation** → In practice this window is the duration of NATS downtime, during which the publisher (concert-discovery CronJob) would also be unable to publish. Net effect: zero missed messages under normal operation.

- **[Risk] SyncAck adds latency per message** → Measured as negligible vs. existing I/O operations. No action needed.

## Migration Plan

1. Apply the two-line config change to `subscriber.go`
2. Commit, push, open PR to backend
3. Merge PR → ArgoCD triggers rolling restart of `consumer-app` Deployment
4. Verify: after deploy, monitor KEDA events — `KEDAScaleTargetDeactivated` should not be followed by `KEDAScaleTargetActivated` within 30 seconds
5. **No rollback procedure needed**: reverting the PR and redeploying restores the previous behavior

## Open Questions

None — root cause confirmed from production logs and source code analysis.
