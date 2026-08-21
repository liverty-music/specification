## MODIFIED Requirements

### Requirement: Resilient Scheduling on Shared Spot Node Pool

The Zitadel API (`zitadel-api`) and Web (`zitadel-web`) Deployments SHALL each be authored against the base manifest with a `PodDisruptionBudget`, a readiness probe pointed at the component's health endpoint (`/debug/ready` for API; `/ui/v2/login` for Web), and a rolling update strategy of `maxUnavailable: 0`. The base manifest MAY be single-replica for cost-simplicity; the `dev` overlay MAY run `replicaCount: 1` with PDB `minAvailable: 0` per the `optimize-dev-gke-cost` change. The **`prod` overlay SHALL explicitly set `replicaCount: 2` and PDB `minAvailable: 1`** for `zitadel-api`, and the running prod state SHALL match it — a prod `zitadel-api` observed at `replicas: 1` is a drift to be corrected, not an accepted posture. `podAntiAffinity` is OPTIONAL at the current resource size (GKE Autopilot rejects it below the CPU floor); it is a node-failure concern separate from the per-process wedge that ≥2 replicas address.

The readiness probe (`/debug/ready`) protects traffic against **startup and migration** unreadiness only. **Neither the readiness probe nor the liveness probe (`/debug/healthz`) detects the in-process projection-trigger wedge (zitadel/zitadel#10103): a wedged pod keeps both `/debug/ready` and `/debug/healthz` at 200 while auth-flow requests hang, so neither probe removes or restarts it.** There is **no automatic recovery** from that wedge — recovery is **manual** (`kubectl rollout restart deploy/zitadel-api`) until the upstream bug is fixed. The prod ≥2-replica posture exists to bound the wedge blast radius to a single pod and to keep one replica serving login while the wedged pod is manually restarted.

**Rationale**: Both overlays target the shared Spot node pool pre-launch. In `dev`, the `optimize-dev-gke-cost` change runs a single replica with a relaxed PDB and accepts a brief auth outage per node event for cost savings. The 2026-06-23 prod outage showed that a single wedged replica (prod was running 1) takes down all login because neither readiness nor liveness can detect the wedge — hence the explicit prod `replicaCount: 2` clause. A self-healing watchdog CronJob (probe the auth flow, auto rollout-restart on hang) was trialled for automatic recovery but **removed as ineffective**; recovery is now a manual rollout restart. Two replicas do not auto-heal (a wedged-but-ready pod still serves and hangs ~half of logins), but they keep one replica serving while an operator restarts the wedged pod.

#### Scenario: Prod runs two replicas

- **WHEN** an operator inspects the running `zitadel-api` Deployment in `prod`
- **THEN** its `spec.replicas` SHALL be 2 and its PDB `minAvailable` SHALL be 1
- **AND** a value of 1 SHALL be treated as drift and reconciled

#### Scenario: Single-replica dev Deployment drains cleanly during node upgrade

- **WHEN** the `dev` overlay runs `replicaCount: 1` with PDB `minAvailable: 0`
- **AND** a node upgrade evicts the node hosting the Zitadel pod
- **THEN** the eviction SHALL succeed (PDB does not block)
- **AND** the Deployment SHALL re-schedule the pod onto another spot node
- **AND** the auth outage during this gap SHALL be acceptable per the dev cost posture

#### Scenario: Unready pod is excluded from Gateway backend

- **WHEN** a Zitadel pod is starting or running a migration
- **THEN** its readiness probe SHALL return non-200 until ready
- **AND** the Gateway SHALL NOT route traffic to that pod until the probe succeeds

#### Scenario: Wedged-but-ready pod is recovered by the watchdog, not readiness

- **WHEN** a `zitadel-api` pod is suffering the projection-trigger wedge (auth-flow requests hang) but `/debug/ready` and `/debug/healthz` still return 200
- **THEN** neither probe SHALL remove or restart the pod (neither detects the wedge) and the Gateway SHALL continue routing to it
- **AND** there is **no automatic recovery**: recovery SHALL be a manual `kubectl rollout restart deploy/zitadel-api`, with the second replica absorbing traffic during the rolling restart
