## MODIFIED Requirements

### Requirement: Self-healing watchdog auto-restarts a wedged Zitadel API

The prod environment SHALL run an in-cluster watchdog that detects the Zitadel projection-trigger wedge (zitadel/zitadel#10103) and automatically restarts the `zitadel-api` Deployment without operator action. The watchdog SHALL be a Kubernetes `CronJob` modeled on the existing dev restart CronJob pattern (a container image carrying `curl` and `kubectl`, plus a dedicated ServiceAccount and a `Role`/`RoleBinding` scoped to `get`/`patch` on the `zitadel-api` Deployment in the `zitadel` namespace only) — NOT a compiled application.

The watchdog SHALL detect the wedge using a **read-only call that exercises the wedged trigger-on-read path**, NOT a `/debug/healthz` or `/debug/ready` check (both return 200 during the wedge). The reference signal is the Connect/gRPC `zitadel.project.v2.ProjectService/ListProjectRoles` method (HTTP+JSON `POST`) against a static project id, which calls `SearchProjectRoles(…, shouldTriggerBulk=true, …)` and so triggers `ProjectRoleProjection.Trigger(WithAwaitRunning())` — the projection observed wedging on 2026-06-23 — as a pure read (no eventstore write). The call returns quickly when healthy and hangs past the gateway timeout when wedged. The probe MUST present a valid credential: unauthenticated calls return `401` before the trigger runs and cannot detect the wedge. The probe SHALL NOT use a write endpoint (e.g. `/oauth/v2/authorize`) and SHALL NOT hardcode a product/consumer OIDC client id.

The probe credential SHALL be a **dedicated, least-privilege machine-user Personal Access Token** (scoped only to the project-role read needed by `ListProjectRoles`, never a shared admin identity), provisioned out of band, stored in Google Secret Manager, synced into the `zitadel` namespace via External Secrets, and mounted into the CronJob as a bearer token. The credential failure mode SHALL be fail-safe: an invalid/expired PAT returns a fast `401` that the watchdog treats as "responded" (no false restart); to avoid silently losing detection, the PAT SHALL be long-lived and its expiry tracked, and a `401`/`403` from the probe SHALL be logged distinctly.

The watchdog SHALL be **conservative against false restarts**:
- It SHALL restart only after **N consecutive hanging probes within a single run** (no single transient blip triggers a restart).
- It SHALL restart only when `/debug/healthz` returns `200` at probe time (the wedge signature is "core healthy AND the read-only trigger path hung"); if core health is also failing it SHALL NOT restart, since the fault is not the wedge.
- It SHALL use `concurrencyPolicy: Forbid` so runs never overlap.

#### Scenario: Wedged pod is auto-restarted

- **WHEN** the authenticated `ListProjectRoles` probe hangs past the gateway timeout for N consecutive probes in one run while `/debug/healthz` returns 200
- **THEN** the watchdog SHALL run the equivalent of `kubectl rollout restart deploy/zitadel-api` in the `zitadel` namespace
- **AND** a fresh `ListProjectRoles` probe SHALL return a normal response within normal latency after the new pod becomes Ready

#### Scenario: Probe is read-only (no auth-request writes)

- **WHEN** the watchdog runs its healthy probes over time
- **THEN** it SHALL create no OIDC auth requests or other eventstore writes (the probe is a read query)

#### Scenario: Transient blip does not trigger a restart

- **WHEN** a single probe in a run hangs but the remaining probes in the same run return normally
- **THEN** the watchdog SHALL NOT restart the Deployment

#### Scenario: Full outage (core health down) does not trigger a restart

- **WHEN** the probe fails AND `/debug/healthz` does not return 200 (e.g. gateway/DNS outage, pod not running)
- **THEN** the watchdog SHALL NOT restart the Deployment, because the fault is not the in-process wedge

#### Scenario: Invalid credential is fail-safe (no false restart)

- **WHEN** the watchdog's PAT is missing, expired, or unauthorized so the probe returns `401`/`403` quickly
- **THEN** the watchdog SHALL treat the fast response as "not wedged" and SHALL NOT restart the Deployment
- **AND** it SHALL log the credential failure distinctly so the loss of detection is discoverable

#### Scenario: Healthy steady state issues no restart

- **WHEN** the `ListProjectRoles` probe returns normally within normal latency on every probe
- **THEN** the watchdog SHALL take no action
