## Context

Self-hosted Zitadel (`ghcr.io/zitadel/zitadel:v4.14.0`, 1 prod replica, `db-f1-micro` Cloud SQL) periodically hits an in-process projection-trigger wedge (zitadel/zitadel#10103). When wedged, every auth-flow query that triggers-on-read a projection hangs until the gateway times out (504), but all health/diagnostic surfaces stay green:

```
healthy & green during wedge          wedged (hangs 20s → 504)
/debug/healthz       200 0.1s         /oauth/v2/authorize   (auth-request projection)
/debug/ready         200 0.1s         searchProjectRoles    (project_roles projection)
/.well-known/openid  200 0.1s         → token/userinfo role assertion
```

Because liveness/readiness only check `/debug/*`, Kubernetes never restarts the wedged pod; recovery is a manual `kubectl rollout restart`. The 2026-06-23 incident ran ~13 min until a human restarted. This design adds an in-cluster self-healing loop so the wedge auto-recovers, and removes the single-replica SPOF — entirely in `cloud-provisioning` (no runtime code change).

Empirical findings that shaped the design (verified 2026-06-23 against prod):
- `/oauth/v2/authorize` with **valid** params (prod consumer client `373015520582107291`, redirect `https://liverty-music.app/auth/callback`) returns **302 in ~0.2s** healthy and **hangs ≥ gateway timeout** when wedged.
- The same endpoint with **invalid/missing** params returns **400 in ~0.15s** — param validation runs *before* the wedged projection code, so a probe must use valid params to reach (and detect) the wedge.
- The OTLP collector's `filter/drop_workload_noise` drops `^rpc\.server\..*$`, and the dormant OIDCService latency alert is commented out because the metric is absent and a missing-metric AlertPolicy 404s the whole prod `pulumi up`. → a metric-based notification alert is not viable cheaply; deferred.

## Goals / Non-Goals

**Goals:**
- Auto-recover from the wedge without human action, target time-to-recovery ≤ ~2 min.
- Detect the wedge via a signal that actually exercises the wedged auth-flow path (not `/debug/*`).
- Limit blast radius to a single pod (prod ≥2 replicas, non-disruptive restarts).
- Be conservative: no restart-looping of a healthy pod; reuse the proven dev CronJob pattern; introduce no compiled application.

**Non-Goals:**
- Fixing zitadel#10103 upstream (tracked separately; this bounds impact only).
- A notification AlertPolicy (deferred — see Context; the metric is dropped at the collector).
- Changing Cloud SQL tier (`db-f1-micro`) — confirmed not the cause (DB clean, connections flat).
- Any `backend`/`frontend`/`specification`-runtime change.

## Decisions

### D1. Detection signal: `curl /oauth/v2/authorize` with valid params, guarded by `/debug/healthz`
The watchdog issues `curl --max-time T` to `/oauth/v2/authorize?...` with valid prod-consumer params and treats a **timeout (curl exit / HTTP 000)** as the wedge signal; a `302` is healthy. To avoid restarting during unrelated outages, it first confirms `/debug/healthz` returns `200` — the wedge signature is specifically "core health green **and** authorize hung". Alternatives considered:
- `/debug/healthz` / `/debug/ready` only — **rejected**: stay 200 during the wedge (root of the gap).
- `/oauth/v2/authorize` with *invalid* params — **rejected**: returns 400 *before* the wedged code, so it can never detect the wedge.
- Pointing a **Kubernetes liveness probe** at authorize — **rejected**: an httpGet liveness treats `400` as failure (so a misconfigured/expired client → restart loop), cannot distinguish a hang from a fast error, and fires a write side-effect every probe period. A CronJob with `curl` can match the *hang* specifically and probe far less often.

### D2. Remediation mechanism: small CronJob (curl + kubectl), reusing the dev restart pattern
A CronJob runs every ~1 min (`concurrencyPolicy: Forbid`), probes N times within one run (e.g. 3 probes ~5s apart), and runs `kubectl rollout restart deploy/zitadel-api` only if **all N hang**. It is the same shape as the existing dev `cronjob-restart-zitadel.yaml` (image with `kubectl`, dedicated ServiceAccount + Role scoped to `deployments` get/patch in the `zitadel` namespace) — just trigger-on-hang instead of weekly-timer. No compiled application. Rejected: a separate controller/Deployment (heavier, stateful) and an alert-driven webhook remediation (depends on the dropped-metric alert path).

### D3. False-restart guards (stateless)
- **N-of-N in-run hangs** (a single transient blip never restarts).
- **`/debug/healthz`=200 precondition** (don't restart during a full outage / network failure where restart wouldn't help).
- **`concurrencyPolicy: Forbid`** (no overlapping runs).
- No stateful cooldown/counter: a `rollout restart` reliably clears #10103, and `maxUnavailable: 0` rolling on 2 replicas keeps it non-disruptive, so a re-run after a genuine still-wedged state legitimately restarts again rather than masking a persistent failure.

### D4. Prod replica posture: explicit ≥2 replicas
The prod overlay SHALL explicitly set `replicaCount: 2` and PDB `minAvailable: 1` (base is single-replica for dev cost-simplicity). Anti-affinity is *not* required for this change: the wedge is per-process, so two replicas on any node(s) already give login redundancy; node-failure topology is a separate concern (and base dropped anti-affinity due to the Autopilot CPU-≥500m constraint at this resource size). Note the nuance: readiness (`/debug/ready`) does **not** drain a wedged-but-ready pod, so 2 replicas alone do not auto-heal — they bound blast radius and make the watchdog's rolling restart non-disruptive. Replicas and watchdog are complementary.

### D5. No notification alert (this change)
Dropped per Context: the latency metric is filtered at the collector and the AlertPolicy 404s the prod stack when the metric is absent. With the watchdog auto-recovering, notification is deferred to a follow-up that can use a viable signal (e.g. a log-based metric on the watchdog's restart action, or Gateway 504 rate).

## Risks / Trade-offs

- **Watchdog restart-loops a healthy pod** → Mitigation: N-of-N in-run hangs + `/debug/healthz`=200 guard + `concurrencyPolicy: Forbid`; probe timeout tuned above normal latency (~0.2s) but below the gateway timeout.
- **Probe side-effect: ~1440 throwaway auth-request event-streams/day** in the eventstore, adding minor load to the very projection path that wedges → Mitigation: 1/min cadence (not per-liveness-tick); read-only probe target is a documented follow-up.
- **Hardcoded prod consumer `client_id`/`redirect_uri`** could break the probe if the consumer app is reprovisioned → Mitigation: documented in the manifest + runbook; a dedicated long-lived "probe" OIDC client is a possible hardening.
- **Probe goes through the public gateway**, so a gateway/DNS outage reads as a hang → Mitigation: the `/debug/healthz`=200 guard (served over the same gateway) gates the restart; if the gateway is down, healthz also fails and no restart fires.
- **New container image** (needs both `curl` and `kubectl`) → Mitigation: pin a well-known image at the cluster k8s minor (e.g. `alpine/k8s:1.32.x`), matching the dev CronJob's intent.

## Migration Plan

1. Bump prod `zitadel-api` to 2 replicas + PDB `minAvailable: 1` (independent, low risk).
2. Add the watchdog CronJob + RBAC to the prod overlay in **dry-run/observe mode** (probe + log the decision, but skip the `rollout restart`) for one soak window to confirm zero false positives.
3. Flip the watchdog to active (restart-enabled) once dry-run shows clean probing.

Rollback: each step is independently revertible — scale back to 1, or `suspend: true` the CronJob to disable auto-restart instantly without deleting it.

## Open Questions

- Read-only probe target that still triggers the wedged projection (to eliminate the auth-request side-effect)?
- Should the follow-up notification alert use a watchdog-restart log-based metric or Gateway 504 rate?
- Is a dedicated long-lived "probe" OIDC client worth provisioning to decouple the watchdog from the consumer app's `client_id`?
