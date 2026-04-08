## Why

After the GKE cluster migration to `standard-cluster-osaka` on 2026-04-01, NATS JetStream started with a fresh PVC (no consumer history). Two bugs in the consumer's NATS subscriber configuration combined to create an infinite message redelivery loop that has been causing Places API overcalls ($323,198 charge) for 3+ days: (1) `DeliverAll()` caused all past messages to be redelivered upon durable consumer recreation, and (2) `AckAsync: true` caused Acks to be lost when KEDA deactivated both consumer pods simultaneously, keeping the JetStream lag > 0 and triggering immediate pod re-activation.

## What Changes

- Remove `AckAsync: true` from `JetStreamConfig` to switch from fire-and-forget `m.Ack()` to synchronous `m.AckSync()`, ensuring Acks are confirmed by NATS server before the handler returns
- Replace `nats.DeliverAll()` with `nats.DeliverNew()` in `SubscribeOptions` to prevent past messages from being redelivered when a durable consumer is created for the first time (e.g., after cluster migration or NATS PVC recreation)

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `auto-concert-discovery`: The consumer reliability guarantee changes — messages are now delivered at-most-once-from-history (DeliverNew) with guaranteed Ack delivery (SyncAck), preventing duplicate concert notifications caused by NATS state loss events.

## Impact

- **backend**: `internal/infrastructure/messaging/subscriber.go` — two-line config change
- **No proto changes**: This is a pure infrastructure/configuration fix
- **No DB migration**: No schema changes
- **Operational**: Fixes the ongoing Places API cost spike; after deploy, KEDA consumer lag should reach 0 and stay there
