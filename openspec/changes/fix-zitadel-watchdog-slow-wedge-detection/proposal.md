# Fix Zitadel wedge: time-based detection, watchdog removal, root cause resolved

## Why

The prod `zitadel-api` deployment periodically entered a projection-trigger wedge
(zitadel/zitadel#10103): `Trigger(WithAwaitRunning())` blocked on a projection
handler that was occupied, causing logins to hang and return HTTP 500. The
`/debug/healthz` and `/debug/ready` endpoints kept returning 200 throughout, so
neither the kubelet nor the existing watchdog CronJob detected the wedge.

Investigation revealed the immediate cause was compounded:
1. **SMTP was INACTIVE for an extended period** → notification events accumulated
   as failures in the `projections.notifications` handler retry queue.
2. **A DB position rollback** (`current_states.position` for
   `projections.notifications` was set to a past value) caused the handler to
   re-scan ~5,994 eventstore events, monopolising `MaxOpenConns: 3` for
   extended periods.
3. **Login triggers (`Trigger(WithAwaitRunning())`)** needed a DB connection, but
   the pool was exhausted by the notifications handler → connection timeout →
   QUERY-5Ngd9 → HTTP 500 → wedge.

## What Changed

**Phase 1 — time-based hang detection (shipped then superseded):**
The CronJob watchdog's hang classifier was widened from `http_code=000`-only to
time-based (`000` OR `time_total >= WATCHDOG_SLOW_SEC` (8s)). This correctly
detected the wedge but the CronJob still issued `rollout restart` on both
replicas simultaneously, producing full-outage windows every restart cycle.

**Phase 2 — per-pod liveness probe sidecar (attempted, then reverted):**
The CronJob was replaced with a `watchdog-probe` sidecar container carrying an
exec liveness probe using the same time-based check. Discovered in prod that a
K8s exec liveness probe failure restarts **only the container that owns the
probe**, not the other containers in the pod — so `watchdog-probe` entered
CrashLoopBackOff while the wedged `zitadel` container ran on unaffected. The
sidecar was reverted (cp#429). Both the CronJob and sidecar are removed.

**Phase 3 — root cause resolved (final state):**
- SMTP was reactivated (cloud-provisioning pulumi up v221), stopping the
  accumulation of failed notification events.
- The `projections.notifications` position was advanced to the current eventstore
  head (`position = 1787110216`), releasing the handler from its backlog and
  freeing the DB connection pool.
- Wedge stopped immediately and did not recur (5-minute clean window confirmed).
- No automated watchdog is needed: under normal operation (SMTP active, no
  projection position rollback) the wedge does not occur.

## Impact

- **REMOVED** from `zitadel-self-hosted-deployment`: "Self-healing watchdog
  auto-restarts a wedged Zitadel API" — the requirement is removed because
  (a) no watchdog implementation was viable within K8s constraints, and
  (b) the root cause is resolved.
- **cloud-provisioning**: `cronjob-watchdog-zitadel.yaml`,
  `external-secret-watchdog-probe-pat.yaml`, `zitadel-api-liveness-sidecar-patch.yaml`
  all removed (cp#415 → cp#425 → cp#429).
- Recovery if wedge ever recurs: `kubectl -n zitadel rollout restart deploy/zitadel-api`.
  Check `projections.notifications` position vs latest eventstore position; if far
  behind, advance position rather than rolling back.
