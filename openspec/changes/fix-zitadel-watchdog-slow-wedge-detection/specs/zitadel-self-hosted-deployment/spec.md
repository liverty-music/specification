## REMOVED Requirements

### Requirement: Self-healing watchdog auto-restarts a wedged Zitadel API

**Reason**: No watchdog implementation proved viable within Kubernetes constraints,
and the root cause of the wedge was resolved, making an automated watchdog
unnecessary.

Two approaches were attempted and removed:
1. **CronJob watchdog** (`kubectl rollout restart`) restarted both replicas
   simultaneously, causing full-outage windows on every detection cycle.
2. **Per-pod liveness probe sidecar** — a K8s exec liveness probe failure restarts
   only the container that owns the probe, not other containers in the pod. The
   `watchdog-probe` sidecar entered CrashLoopBackOff while the wedged `zitadel`
   container ran on unaffected.

The actual wedge (projection-trigger deadlock from an exhausted DB connection pool
driven by a `projections.notifications` handler stuck in a backlog) was resolved
by fixing the root cause: SMTP reactivated (no new notification failures) and the
`projections.notifications` position advanced to the current eventstore head
(freeing the connection pool). The wedge has not recurred.

Recovery if the wedge ever occurs: `kubectl -n zitadel rollout restart deploy/zitadel-api`.
Investigate `projections.notifications` position vs latest eventstore position; if
far behind, advance position forward rather than rolling back.
