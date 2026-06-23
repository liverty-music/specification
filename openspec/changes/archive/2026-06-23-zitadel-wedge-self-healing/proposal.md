## Why

On 2026-06-23 production hosted login was fully down for ~13 minutes (05:47–06:00 UTC): the self-hosted Zitadel API hit a projection-trigger wedge (upstream zitadel/zitadel#10103, unfixed in v4.14.0) where an in-process trigger-on-read deadlock hung every auth-flow query (`/oauth/v2/authorize`, `searchProjectRoles`) while `/debug/healthz`, `/debug/ready`, OIDC discovery, and static assets all stayed 200/fast. Two latent gaps turned a known, self-recoverable bug into a manual outage:

1. **No self-healing** — the wedge clears only on `kubectl rollout restart deploy/zitadel-api`. Liveness (`/debug/healthz`) and readiness (`/debug/ready`) both keep returning 200 during the wedge, so Kubernetes never restarts the wedged pod. Recovery required a human; the outage ran until one restarted it by hand.
2. **Single point of failure** — prod `zitadel-api` runs **1 replica**, so a single wedged process = total login outage with no replica to absorb traffic during recovery.

This is the second recurrence of this incident class; restarting by hand when a user complains is not an acceptable steady state.

## What Changes

- Add a **self-healing watchdog** — a small in-cluster CronJob (the same pattern as the existing dev weekly-restart CronJob: `curl` + `kubectl`, no compiled application) that probes a real auth-flow endpoint and, on a sustained hang, automatically runs `rollout restart deploy/zitadel-api`. This converts a multi-minute manual outage into unattended recovery within ~2 minutes.
- Bring **prod `zitadel-api` to ≥2 replicas** so a single-process wedge degrades rather than fully outages login, and the watchdog's rolling restart is non-disruptive.

Explicitly **out of scope** (decided during exploration): a notification AlertPolicy. The previously-specced OIDCService p99-latency alert depends on `rpc.server.duration`, which the OTLP collector intentionally drops for cost (`filter/drop_workload_noise`), so it cannot fire without re-enabling that metric; with the watchdog auto-recovering, a notification alert is deferred to a follow-up.

## Capabilities

### New Capabilities
<!-- none — the self-healing behavior extends the existing deployment capability rather than introducing a new bounded capability. -->

### Modified Capabilities
- `zitadel-self-hosted-deployment`: add a requirement for the in-cluster self-healing watchdog (auth-flow hang probe → automatic `zitadel-api` restart), and tighten the resilient-scheduling requirement so the **prod** overlay explicitly runs ≥2 `zitadel-api` replicas and so wedge-recovery is delegated to the watchdog (readiness cannot detect the wedge).

## Impact

- **Repo**: `cloud-provisioning` only (Kustomize overlay for `zitadel` prod: a watchdog CronJob + RBAC, and a `replicaCount`/PDB bump). No `backend`/`frontend`/`specification`-runtime code changes.
- **Cluster**: prod `zitadel` namespace — one new CronJob workload + a dedicated ServiceAccount/Role/RoleBinding scoped to restarting the `zitadel-api` Deployment, plus a second `zitadel-api` replica.
- **Cost**: marginal (a 1/min short-lived CronJob pod + one extra zitadel-api replica on the shared Spot pool).
- **Side effect**: the probe hits `/oauth/v2/authorize` with valid params, creating a short-lived throwaway auth request per probe (~1440/day) in the eventstore. Acceptable pre-launch; a read-only probe target is a documented follow-up.
- **Risk**: a mis-tuned watchdog could restart-loop. Mitigated by requiring N consecutive in-run hangs, a `/debug/healthz`=200 guard (only the wedge signature triggers a restart), and `concurrencyPolicy: Forbid`. Detailed in design.md.
- **Upstream**: does not fix zitadel#10103; it bounds the operational impact until an upstream fix is pinned.
