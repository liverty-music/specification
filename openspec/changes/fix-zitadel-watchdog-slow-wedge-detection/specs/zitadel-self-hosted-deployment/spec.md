## MODIFIED Requirements

### Requirement: Self-healing watchdog auto-restarts a wedged Zitadel API

The prod environment SHALL detect the Zitadel projection-trigger wedge
(zitadel/zitadel#10103) and automatically restart affected `zitadel-api` pods
without operator action.

**Detection mechanism:** The watchdog SHALL use a **read-only call that exercises
the wedged trigger-on-read path**, NOT `/debug/healthz` or `/debug/ready` (both
return 200 during the wedge). The reference signal is the Connect/gRPC
`zitadel.project.v2.ProjectService/ListProjectRoles` method (HTTP+JSON `POST`)
against a static project id, which calls
`SearchProjectRoles(…, shouldTriggerBulk=true, …)` and triggers
`ProjectRoleProjection.Trigger(WithAwaitRunning())` — the projection observed
wedging on 2026-06-23 — as a pure read (no eventstore write). The call returns
quickly (well under a second) when healthy. When wedged the trigger-on-read
blocks and surfaces as either a full client timeout (`http_code=000`) or a slow
error/response at the server's internal ~10s deadline. The probe MUST present a
valid credential (unauthenticated calls return `401` before the trigger runs and
cannot detect the wedge). The probe SHALL NOT use a write endpoint and SHALL NOT
hardcode a product/consumer OIDC client id.

**Hang classification:** Detection SHALL be **time-based**, not HTTP-code-based.
A probe counts as a hang when its total time crosses a configured slow-response
threshold (whole seconds, default 8s) **OR** it times out entirely
(`http_code=000`). This captures both wedge manifestations. The client request
timeout SHALL be set above the server's internal deadline (e.g. 12s vs ~10s) so
a slow error is captured with its timing. A fast response — healthy sub-second
`2xx`, or a fast transient error below the threshold — SHALL NOT be counted as a
hang.

**Implementation:** The watchdog SHALL be implemented as a **per-pod `exec`
liveness probe on a `curl`-capable sidecar container** added to the `zitadel-api`
pod spec — NOT a cluster-wide CronJob. The sidecar approach ensures each pod
restarts **independently** based on its own probe result, naturally
desynchronising the two replicas so at least one is always healthy while the
other recovers. A CronJob issuing `rollout restart` restarts both replicas
simultaneously, creating a full outage window on every wedge detection cycle.

The probe credential SHALL be a **dedicated, least-privilege machine-user Personal
Access Token** (scoped only to the project-role read needed by `ListProjectRoles`,
never a shared admin identity), stored in Google Secret Manager, synced into the
`zitadel` namespace via External Secrets, and mounted into the `zitadel-api` pod
as a bearer token. The credential failure mode SHALL be fail-safe: a fast `401`
is treated as "not wedged" (no restart), and `401`/`403` SHALL be logged
distinctly.

The watchdog SHALL be **conservative against false restarts**:
- It SHALL restart only after **N consecutive hanging probes** (`failureThreshold`).
- A **fast** response SHALL NOT be counted as a hang.
- It SHALL use K8s-native `initialDelaySeconds` to avoid restarting during pod
  startup/warmup before the projection is ready.

#### Scenario: Wedged pod is auto-restarted

- **WHEN** the authenticated `ListProjectRoles` probe hangs (times out, or returns
  at/after the slow threshold) for N consecutive probes
- **THEN** the K8s liveness probe fails and the kubelet restarts that pod
- **AND** a fresh `ListProjectRoles` probe SHALL return a normal response within
  normal latency after the new pod becomes Ready

#### Scenario: Slow 5xx just under the client timeout is detected as a wedge

- **WHEN** the `ListProjectRoles` probe returns a slow error whose total time is
  at or above the slow threshold but below the client timeout (server's internal
  deadline fired before the client timed out) for N consecutive probes
- **THEN** the watchdog SHALL treat each such probe as a hang and SHALL restart
  the pod
- **AND** it SHALL NOT rely on `http_code=000` to make that decision

#### Scenario: Replicas restart independently — no full-outage window

- **WHEN** one `zitadel-api` pod is wedged and its liveness probe fails
- **THEN** only that pod is restarted by the kubelet; the other pod continues
  serving traffic
- **AND** the PDB (`minAvailable: 1`) enforces that at least one replica remains
  Ready throughout

#### Scenario: Probe is read-only (no auth-request writes)

- **WHEN** the watchdog runs its healthy probes over time
- **THEN** it SHALL create no OIDC auth requests or other eventstore writes

#### Scenario: Transient blip does not trigger a restart

- **WHEN** a single probe in a series hangs but the remaining probes return normally
- **THEN** the watchdog SHALL NOT restart the pod (`failureThreshold` not reached)

#### Scenario: Fast transient error does not trigger a restart

- **WHEN** a probe returns an error status whose total time is below the slow
  threshold
- **THEN** the watchdog SHALL NOT count that probe as a hang

#### Scenario: Invalid credential is fail-safe (no false restart)

- **WHEN** the watchdog's PAT is missing, expired, or unauthorized (`401`/`403`)
- **THEN** the watchdog SHALL treat the fast response as "not wedged", SHALL NOT
  restart the pod, and SHALL log the credential failure distinctly

#### Scenario: Full outage (core health down) does not trigger a restart

- **WHEN** the probe fails AND core health is also down (e.g. gateway/DNS outage, pod not running, init failure) — not the in-process wedge signature
- **THEN** the liveness probe exec script's healthz-precondition guard (checking `/debug/healthz` before counting hangs) ensures a gateway-level failure is not mistaken for the wedge; non-wedge failures are handled by existing readiness/startup probe lifecycle, not this liveness probe

#### Scenario: Healthy steady state issues no restart

- **WHEN** the `ListProjectRoles` probe returns normally within normal latency
- **THEN** the watchdog SHALL take no action
