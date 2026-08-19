# Fix the Zitadel wedge watchdog: time-based detection + per-pod liveness probe sidecar

## Why

The self-healing watchdog (`zitadel-self-hosted-deployment` capability) exists
to auto-restart a `zitadel-api` pod caught in the projection-trigger wedge
(zitadel/zitadel#10103, still OPEN upstream as of v4.17.x — no fix shipped).
It detects the wedge by probing `ProjectService/ListProjectRoles` and treating
a probe that "hangs past the gateway timeout" as the wedge signal.

**Problem 1 — detection gap:** The prod manifest implemented "hang" too narrowly:
it counted a probe as hung **only when `curl` returned `http_code=000`** (a full
client-side timeout at `--max-time 10`). But the wedge does not always time the
client out. When the projection trigger blocks, Zitadel's own internal ~10s
deadline frequently fires **first**, returning a **slow HTTP 500 at ~9.9s** —
just under the old `--max-time 10`. That is a real wedge, yet `http_code=000`
never matched, so `hangs` stayed at 0 and the watchdog **never restarted the
pod**. This was observed directly (test-organizer Deactivate; RemoveUser wedged;
ListProjectRoles returned slow 500s; healthz stayed 200; watchdog took no action).

**Problem 2 — structural availability gap:** The CronJob-based watchdog issues
`kubectl rollout restart`, which replaces **both replicas simultaneously**. The
~90s rollout window leaves the service fully unavailable. Worse, because both
replicas restart in lockstep they also re-wedge in lockstep (~3 min after each
restart), causing repeated complete outages. Post-deployment observation confirmed
this: Cloud Logging showed `http_code=000` at 180/180 probes per hour (100% wedge)
from 2026-08-17T13:00 through 2026-08-18T05:00 with **zero restarts** (old 000-only
check never fired), then ~20 CronJob-triggered restarts/hour after the detection
fix — improving availability from 0% to ~50%, but still with periodic full-outage
windows from the synchronised restart pattern.

A per-pod liveness probe restarts each replica **independently**, naturally
desynchronising them so at least one replica is always in its healthy post-startup
window while the other restarts.

## What Changes

**Phase 1 (shipped 2026-08-18):** Time-based hang detection in the existing CronJob.
- **MODIFIED** `zitadel-self-hosted-deployment` — redefine "hang" as time-based:
  a probe counts as hung when its total time crosses `WATCHDOG_SLOW_SEC` (8s) OR
  it times out entirely (`http_code=000`). Client `--max-time` raised to 12s (above
  the server's ~10s internal deadline) so a slow error is captured with its timing.
  Fast responses are still NOT hangs (conservative-against-false-restarts preserved).

**Phase 2 (planned):** Replace the CronJob watchdog with a per-pod liveness probe sidecar.
- A `curl`-capable sidecar container is added to the `zitadel-api` pod spec. A K8s
  `exec` liveness probe on that sidecar runs the same time-based `ListProjectRoles`
  check (same WATCHDOG_SLOW_SEC threshold, same PAT credential). Each pod restarts
  **independently** on wedge detection, eliminating the synchronised restart window
  and keeping at least one replica healthy at all times.
- The CronJob, its ServiceAccount, RoleBinding, Role, and standalone ExternalSecret
  are removed. The PAT secret is retargeted to the `zitadel-api` pod itself.

## Impact

- Affected capability: `zitadel-self-hosted-deployment` (watchdog requirement).
- Affected code (Phase 1, complete):
  - `cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/cronjob-watchdog-zitadel.yaml`
    (probe loop reads `%{time_total}`; `--max-time 10 → 12`; `sleep 5 → 3`;
    new `WATCHDOG_SLOW_SEC` env).
- Affected code (Phase 2, planned):
  - Add liveness probe sidecar to `zitadel-api` Deployment (Helm values / overlay patch).
  - Remove `cronjob-watchdog-zitadel.yaml` and standalone `external-secret-watchdog-probe-pat.yaml`.
- Prod-only; the wedge and the watchdog are prod concerns.
- Temporary: removed entirely when upstream zitadel/zitadel#10103 ships and is pinned.
