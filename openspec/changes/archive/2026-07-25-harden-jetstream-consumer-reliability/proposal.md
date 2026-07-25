## Why

A single mis-configured JetStream durable silently stopped **all** backend event consumption from ~2026-07-01 to 2026-07-09 (push notifications, analytics forwarding, sales reminders). Events were published fine but never consumed; the pod stayed `Running` because liveness only checks an HTTP port, and neither existing alert (`Consumer ERROR Log`, `Consumer Poison Queue Message`) could fire because the failure emitted no ERROR and produced no poison message. The outage went undetected for ~1 week until a user noticed a missing push. We need consumer stalls to be impossible to miss and safe to remediate — and to remove the naming footgun that caused it.

## What Changes

- **Consumer stall detection (highest priority)**: add a Cloud Monitoring alert on JetStream consumer backlog (`num_pending`) so any consumer that stops draining fires an incident within minutes. This is the one control that would have caught the outage immediately.
- **Fail loud, not silent**: a JetStream subscription/bind failure at consumer startup MUST surface as an ERROR log and fail startup (crashloop) instead of being swallowed. This makes the pod restart and lets the existing `Consumer ERROR Log` alert fire.
- **Liveness reflects real consumption**: the consumer health/liveness probe MUST report unhealthy when the message router is not running or expected durables are not bound, so Kubernetes auto-restarts a wedged pod instead of leaving it `Running`.
- **Safe durable config changes**: consumer startup MUST reconcile durables — when a durable's server-stored config has drifted from the desired config (name, deliver group, policy), delete and recreate it — so a naming/config change can never again wedge on a stale pre-existing durable.
- **Name consumers by *behavior*, not by subject.** A subject says *what happened* (`CONCERT.created`); a consumer says *what we do* (`notify-concert`). Durable **and** deliver-group names become the behavior (handler) name from a controlled `<verb>-<object>` vocabulary (`ingest`/`resolve`/`verify`/`notify`/`track`/`log`); analytics forwarders collapse `forward-…-to-analytics` → `track-…`. The invariant that fixes the incident: **each consumer has a unique deliver group (`group == name`)** — no shared `"consumer"` group. **BREAKING**: requires a durable migration via the reconciliation path above; ships only after Phase 1's fail-loud + detection are live.
- **Give every handler its own consumer (fix fan-out).** Two behaviors on one subject (e.g. `ARTIST.created` → resolve-name + resolve-image; `USER.created` → verify-email + analytics) must each receive every message. Today they collapse onto one shared consumer and silently load-balance (only one runs). Build one watermill subscriber per handler over a single shared NATS connection so each behavior is an independent consumer.
- **Normalize subjects to past-tense events + drop the dead `ACCOUNT` stream.** `SALES_PHASE.reminder.due` → `SALES_PHASE.reminder_due`; `ACCOUNT.login` → `USER.logged_in` (the `account.login` webhook was reverted; the `ACCOUNT` stream is vestigial). Subjects are backend Go constants (not proto), so this is backend + KEDA + an analytics-catalog doc update — **no proto/BSR release**.
- **Reconcile KEDA ScaledObject triggers** with the new behavior-based durable names so autoscaling reads real backlog.

## Capabilities

### New Capabilities
- `jetstream-consumer-reliability`: how the backend consumer subscribes to, names, health-checks, and reconciles JetStream durables so a stalled or mis-configured consumer is detected, self-heals, and remains safe to reconfigure — plus the backlog alert and KEDA trigger alignment that make stalls observable.

### Modified Capabilities
<!-- No existing spec's requirements change. The existing `app-error-log-alerting` consumer-ERROR requirement is reused as-is: the fail-loud behavior makes the consumer actually emit an ERROR on subscribe failure, satisfying that requirement without changing it. -->

## Impact

- **backend** (Go): `internal/infrastructure/messaging/subscriber.go` (per-handler subscribers over a shared conn, behavior naming, surface subscribe errors, startup reconciliation), `internal/di/consumer.go` (per-handler wiring), `internal/entity/event_data.go` (subject constants: `reminder.due`→`reminder_due`, `ACCOUNT.login`→`USER.logged_in`), `streams.go` (drop `ACCOUNT`, `SALES_PHASE.>`→`SALES_PHASE.*`), publisher call sites for renamed subjects; consumer health endpoint (:8081) already shipped in Phase 1.
- **cloud-provisioning** (Pulumi/GCP + K8s): consumer `ScaledObject` triggers renamed to the behavior-based durable names (and `USER.logged_in` stream); Phase 1 alert policy + `maxSurge:0` already shipped.
- **specification** (docs only): `docs/analytics/event-catalog.md` subject-name updates. **No proto change; no BSR release.**
- **Operational**: a one-time durable migration (delete all stale shared-group/subject-named/prefixed durables + the dead `ACCOUNT.login`) run through the reconciliation path; documented runbook step for future durable config changes. **This migration also remediates the current prod partial-outage** (shared-group misbind leaving ~10 subjects unconsumed).
