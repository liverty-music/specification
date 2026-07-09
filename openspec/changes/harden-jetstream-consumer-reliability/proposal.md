## Why

A single mis-configured JetStream durable silently stopped **all** backend event consumption from ~2026-07-01 to 2026-07-09 (push notifications, analytics forwarding, sales reminders). Events were published fine but never consumed; the pod stayed `Running` because liveness only checks an HTTP port, and neither existing alert (`Consumer ERROR Log`, `Consumer Poison Queue Message`) could fire because the failure emitted no ERROR and produced no poison message. The outage went undetected for ~1 week until a user noticed a missing push. We need consumer stalls to be impossible to miss and safe to remediate — and to remove the naming footgun that caused it.

## What Changes

- **Consumer stall detection (highest priority)**: add a Cloud Monitoring alert on JetStream consumer backlog (`num_pending`) so any consumer that stops draining fires an incident within minutes. This is the one control that would have caught the outage immediately.
- **Fail loud, not silent**: a JetStream subscription/bind failure at consumer startup MUST surface as an ERROR log and fail startup (crashloop) instead of being swallowed. This makes the pod restart and lets the existing `Consumer ERROR Log` alert fire.
- **Liveness reflects real consumption**: the consumer health/liveness probe MUST report unhealthy when the message router is not running or expected durables are not bound, so Kubernetes auto-restarts a wedged pod instead of leaving it `Running`.
- **Safe durable config changes**: consumer startup MUST reconcile durables — when a durable's server-stored config has drifted from the desired config (name, deliver group, policy), delete and recreate it — so a naming/config change can never again wedge on a stale pre-existing durable.
- **Remove the redundant `consumer_` prefix** from durable and deliver-group names, reverting to bare per-subject names (`CONCERT_created`, `ARTIST_followed`, …). All event consumption is done by the single consumer app, so the prefix carries no information; removing it also re-aligns the KEDA triggers (which already reference bare names) and cleans up the stale orphan durables. **BREAKING**: requires a durable migration, executed via the new reconciliation path above — must ship only after fail-loud + detection are in place.
- **Reconcile KEDA ScaledObject triggers** with the live durable names so autoscaling reads real backlog in dev/staging.

## Capabilities

### New Capabilities
- `jetstream-consumer-reliability`: how the backend consumer subscribes to, names, health-checks, and reconciles JetStream durables so a stalled or mis-configured consumer is detected, self-heals, and remains safe to reconfigure — plus the backlog alert and KEDA trigger alignment that make stalls observable.

### Modified Capabilities
<!-- No existing spec's requirements change. The existing `app-error-log-alerting` consumer-ERROR requirement is reused as-is: the fail-loud behavior makes the consumer actually emit an ERROR on subscribe failure, satisfying that requirement without changing it. -->

## Impact

- **backend** (Go): `internal/infrastructure/messaging/subscriber.go` (drop prefix, surface subscribe errors, startup reconciliation), consumer health endpoint (`/healthz`/`/readyz` on :8081), `internal/di/consumer.go` startup wiring.
- **cloud-provisioning** (Pulumi/GCP + K8s): new Cloud Monitoring alert policy for consumer backlog; consumer `ScaledObject` trigger `consumer` names; consumer Deployment liveness/readiness probe config.
- **Operational**: a one-time durable migration (delete stale orphans + prefix removal) run through the new reconciliation path; documented runbook step for future durable config changes.
- No proto/schema change; no BSR release required.
