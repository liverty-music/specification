## MODIFIED Requirements

### Requirement: Self-healing watchdog auto-restarts a wedged Zitadel API

The prod environment SHALL run an in-cluster watchdog that detects the Zitadel projection-trigger wedge (zitadel/zitadel#10103) and automatically restarts the `zitadel-api` Deployment without operator action. The watchdog SHALL be a Kubernetes `CronJob` modeled on the existing dev restart CronJob pattern (a container image carrying `curl` and `kubectl`, plus a dedicated ServiceAccount and a `Role`/`RoleBinding` scoped to `get`/`patch` on the `zitadel-api` Deployment in the `zitadel` namespace only) — NOT a compiled application.

The watchdog SHALL detect the wedge using a **read-only call that exercises the wedged trigger-on-read path**, NOT a `/debug/healthz` or `/debug/ready` check (both return 200 during the wedge). The reference signal is the Connect/gRPC `zitadel.project.v2.ProjectService/ListProjectRoles` method (HTTP+JSON `POST`) against a static project id, which calls `SearchProjectRoles(…, shouldTriggerBulk=true, …)` and so triggers `ProjectRoleProjection.Trigger(WithAwaitRunning())` — the projection observed wedging on 2026-06-23 — as a pure read (no eventstore write). The call returns quickly (well under a second) when healthy. When wedged the trigger-on-read blocks, and the probe surfaces this in one of two ways depending on the race with the server's own internal request deadline (~10s): either the client times out first (`http_code=000`), or the server returns a **slow error (typically 5xx) — or occasionally a slow 2xx — right at its deadline** (~9–10s). Both are the wedge. The probe MUST present a valid credential: unauthenticated calls return `401` before the trigger runs and cannot detect the wedge. The probe SHALL NOT use a write endpoint (e.g. `/oauth/v2/authorize`) and SHALL NOT hardcode a product/consumer OIDC client id.

The probe credential SHALL be a **dedicated, least-privilege machine-user Personal Access Token** (scoped only to the project-role read needed by `ListProjectRoles`, never a shared admin identity), provisioned out of band, stored in Google Secret Manager, synced into the `zitadel` namespace via External Secrets, and mounted into the CronJob as a bearer token. The credential failure mode SHALL be fail-safe: an invalid/expired PAT returns a fast `401` that the watchdog treats as "responded" (no false restart); to avoid silently losing detection, the PAT SHALL be long-lived and its expiry tracked, and a `401`/`403` from the probe SHALL be logged distinctly.

The watchdog SHALL classify a probe as a **hang using response TIME, not the final HTTP status code**. A probe counts as a hang when its total time crosses a configured slow-response threshold (whole seconds, default 8s) **OR** it times out entirely (`http_code=000`). This deliberately captures both wedge manifestations — the full client timeout AND the slow error/response returned just under the server deadline. The client request timeout SHALL be set **above** the server's internal deadline (e.g. 12s vs ~10s) so that a slow error is captured together with its timing rather than being truncated to a bare `000`. A `401`/`403` is exempt (credential fail-safe, above) and SHALL NOT be counted as a hang.

The watchdog SHALL be **conservative against false restarts**:
- It SHALL restart only after **N consecutive hanging probes within a single run** (no single transient blip triggers a restart).
- A **fast** response — a healthy sub-second `2xx`, or a fast transient error whose total time is below the slow threshold — SHALL NOT be counted as a hang, so unrelated momentary errors do not trigger a restart.
- It SHALL restart only when `/debug/healthz` returns `200` at probe time (the wedge signature is "core healthy AND the read-only trigger path hung"); if core health is also failing it SHALL NOT restart, since the fault is not the wedge.
- It SHALL use `concurrencyPolicy: Forbid` so runs never overlap.

#### Scenario: Wedged pod is auto-restarted

- **WHEN** the authenticated `ListProjectRoles` probe hangs (times out, or returns at/after the slow threshold) for N consecutive probes in one run while `/debug/healthz` returns 200
- **THEN** the watchdog SHALL run the equivalent of `kubectl rollout restart deploy/zitadel-api` in the `zitadel` namespace
- **AND** a fresh `ListProjectRoles` probe SHALL return a normal response within normal latency after the new pod becomes Ready

#### Scenario: Slow 5xx just under the client timeout is detected as a wedge

- **WHEN** the `ListProjectRoles` probe returns a slow error (e.g. HTTP 500) whose total time is at or above the slow-response threshold but below the client request timeout — i.e. the server's internal deadline fired before the client timed out — for N consecutive probes in one run while `/debug/healthz` returns 200
- **THEN** the watchdog SHALL treat each such probe as a hang and SHALL restart the Deployment
- **AND** it SHALL NOT rely on the probe having produced `http_code=000` to make that decision

#### Scenario: Probe is read-only (no auth-request writes)

- **WHEN** the watchdog runs its healthy probes over time
- **THEN** it SHALL create no OIDC auth requests or other eventstore writes (the probe is a read query)

#### Scenario: Transient blip does not trigger a restart

- **WHEN** a single probe in a run hangs but the remaining probes in the same run return normally
- **THEN** the watchdog SHALL NOT restart the Deployment

#### Scenario: Fast transient error does not trigger a restart

- **WHEN** a probe returns an error status (e.g. HTTP 500 or 502) but its total time is below the slow-response threshold (a fast failure, not a wedge)
- **THEN** the watchdog SHALL NOT count that probe as a hang and SHALL NOT restart the Deployment on its account

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
