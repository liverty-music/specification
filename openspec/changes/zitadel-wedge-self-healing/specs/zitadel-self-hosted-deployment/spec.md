## ADDED Requirements

### Requirement: Self-healing watchdog auto-restarts a wedged Zitadel API

The prod environment SHALL run an in-cluster watchdog that detects the Zitadel projection-trigger wedge (zitadel/zitadel#10103) and automatically restarts the `zitadel-api` Deployment without operator action. The watchdog SHALL be a Kubernetes `CronJob` modeled on the existing dev restart CronJob pattern (a container image carrying `curl` and `kubectl`, plus a dedicated ServiceAccount and a `Role`/`RoleBinding` scoped to `get`/`patch` on the `zitadel-api` Deployment in the `zitadel` namespace only) — NOT a compiled application.

The watchdog SHALL detect the wedge using an **auth-flow signal that exercises the wedged trigger-on-read path**, NOT a `/debug/healthz` or `/debug/ready` check (both return 200 during the wedge). The reference signal is an HTTP `GET` to `/oauth/v2/authorize` with **valid** OIDC parameters (a registered prod client id + redirect uri) that returns a `302` quickly when healthy and hangs past the gateway timeout when wedged. Invalid parameters SHALL NOT be used because they return `400` before the wedged code path and cannot detect the wedge.

The watchdog SHALL be **conservative against false restarts**:
- It SHALL restart only after **N consecutive hanging probes within a single run** (no single transient blip triggers a restart).
- It SHALL restart only when `/debug/healthz` returns `200` at probe time (the wedge signature is "core healthy AND auth-flow hung"); if core health is also failing it SHALL NOT restart, since the fault is not the wedge.
- It SHALL use `concurrencyPolicy: Forbid` so runs never overlap.

#### Scenario: Wedged pod is auto-restarted

- **WHEN** `/oauth/v2/authorize` (valid params) hangs past the gateway timeout for N consecutive probes in one run while `/debug/healthz` returns 200
- **THEN** the watchdog SHALL run the equivalent of `kubectl rollout restart deploy/zitadel-api` in the `zitadel` namespace
- **AND** a fresh `/oauth/v2/authorize` SHALL return `302` within normal latency after the new pod becomes Ready

#### Scenario: Transient blip does not trigger a restart

- **WHEN** a single probe in a run hangs but the remaining probes in the same run return `302`
- **THEN** the watchdog SHALL NOT restart the Deployment

#### Scenario: Full outage (core health down) does not trigger a restart

- **WHEN** the authorize probe fails AND `/debug/healthz` does not return 200 (e.g. gateway/DNS outage, pod not running)
- **THEN** the watchdog SHALL NOT restart the Deployment, because the fault is not the in-process wedge

#### Scenario: Healthy steady state issues no restart

- **WHEN** `/oauth/v2/authorize` returns `302` within normal latency on every probe
- **THEN** the watchdog SHALL take no action

## MODIFIED Requirements

### Requirement: Resilient Scheduling on Shared Spot Node Pool

The Zitadel API (`zitadel-api`) and Web (`zitadel-web`) Deployments SHALL each be authored against the base manifest with a `PodDisruptionBudget`, a readiness probe pointed at the component's health endpoint (`/debug/ready` for API; `/ui/v2/login` for Web), and a rolling update strategy of `maxUnavailable: 0`. The base manifest MAY be single-replica for cost-simplicity; the `dev` overlay MAY run `replicaCount: 1` with PDB `minAvailable: 0` per the `optimize-dev-gke-cost` change. The **`prod` overlay SHALL explicitly set `replicaCount: 2` and PDB `minAvailable: 1`** for `zitadel-api`, and the running prod state SHALL match it — a prod `zitadel-api` observed at `replicas: 1` is a drift to be corrected, not an accepted posture. `podAntiAffinity` is OPTIONAL at the current resource size (GKE Autopilot rejects it below the CPU floor); it is a node-failure concern separate from the per-process wedge that ≥2 replicas address.

The readiness probe (`/debug/ready`) protects traffic against **startup and migration** unreadiness only. It SHALL NOT be relied upon to remove a pod suffering the in-process projection-trigger wedge (zitadel/zitadel#10103): a wedged pod keeps `/debug/ready` and `/debug/healthz` at 200 while auth-flow requests hang. Recovery from that wedge is delegated to the self-healing watchdog (see "Self-healing watchdog auto-restarts a wedged Zitadel API"); the prod ≥2-replica posture exists to bound the wedge blast radius to a single pod and to make the watchdog's rolling restart non-disruptive.

**Rationale**: Both overlays target the shared Spot node pool pre-launch. In `dev`, the `optimize-dev-gke-cost` change runs a single replica with a relaxed PDB and accepts a brief auth outage per node event for cost savings. The 2026-06-23 prod outage showed that a single wedged replica (prod was running 1) takes down all login because readiness cannot detect the wedge — hence the explicit prod `replicaCount: 2` clause and the delegation of wedge-recovery to the watchdog. Two replicas alone do not auto-heal (a wedged-but-ready pod still serves and hangs ~half of logins), but they keep one replica serving while the watchdog restarts the other.

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

- **WHEN** a `zitadel-api` pod is suffering the projection-trigger wedge (auth-flow requests hang) but `/debug/ready` still returns 200
- **THEN** the Gateway SHALL continue routing to that pod (readiness does not detect the wedge)
- **AND** recovery SHALL come from the self-healing watchdog restarting the pod, with the second replica absorbing traffic during the rolling restart
