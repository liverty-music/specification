## Why

The self-healing wedge watchdog was removed from production as ineffective, but
`zitadel-self-hosted-deployment` still names it as the recovery mechanism for the
Zitadel projection-trigger wedge (zitadel/zitadel#10103). The spec now describes a
component that no longer exists — the `2026-08-19-fix-zitadel-watchdog-slow-wedge-detection`
change removed the standalone `Self-healing watchdog auto-restarts a wedged Zitadel API`
requirement but left dangling references to it inside `Resilient Scheduling on Shared
Spot Node Pool`. This change reconciles the spec with the shipped reality: no watchdog,
manual rollout restart on wedge, `≥2` prod replicas to bound the blast radius.

## What Changes

- **Reconcile `zitadel-self-hosted-deployment`** — restate the `Resilient Scheduling
  on Shared Spot Node Pool` requirement so it no longer delegates wedge recovery to
  the removed watchdog:
  - The wedge is NOT auto-recovered: **neither the readiness probe (`/debug/ready`)
    nor the liveness probe (`/debug/healthz`) detects it** (both stay `200` while
    auth-flow requests hang). Recovery is **manual** (`kubectl rollout restart
    deploy/zitadel-api`) until zitadel/zitadel#10103 is fixed upstream.
  - The prod `replicaCount: 2` / PDB `minAvailable: 1` posture is **retained** and
    re-justified: `≥2` replicas keep one replica serving while an operator manually
    restarts the wedged pod (they bound the blast radius; they do not self-heal).
  - Replace the `Wedged-but-ready pod is recovered by the watchdog, not readiness`
    scenario with one describing manual recovery.
  - Remove the dangling `(see "Self-healing watchdog auto-restarts a wedged Zitadel API")`
    cross-reference.
- **Tidy the stale watchdog comment** in `cloud-provisioning`
  `k8s/namespaces/zitadel/overlays/prod/values.yaml` (still cites the removed
  `cronjob-watchdog-zitadel.yaml`).
- **Delete the stale duplicate change dir** `openspec/changes/fix-zitadel-watchdog-slow-wedge-detection`
  (byte-identical to the already-archived `2026-08-19-fix-zitadel-watchdog-slow-wedge-detection`).

Non-goals: re-introducing any automatic wedge recovery; changing the replica count
or PDB; touching the dev-only weekly `cronjob-restart-zitadel.yaml` (unrelated to the
watchdog).

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `zitadel-self-hosted-deployment`: the `Resilient Scheduling on Shared Spot Node Pool`
  requirement no longer references the removed self-healing watchdog; wedge recovery is
  documented as manual rollout restart, with the `≥2`-replica prod posture retained to
  bound the blast radius.

## Impact

- **Spec**: `openspec/specs/zitadel-self-hosted-deployment/spec.md` (delta on one
  requirement + its scenario).
- **cloud-provisioning**: stale comment fix in
  `k8s/namespaces/zitadel/overlays/prod/values.yaml` (no manifest/behavior change —
  the watchdog CronJob + probe-PAT external-secret were already removed).
- **No runtime/behavior change**: production already runs without the watchdog; this
  aligns the written spec (and one code comment) with that shipped state.
