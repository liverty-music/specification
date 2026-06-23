## Context

The shipped watchdog (`zitadel-wedge-self-healing`) probes `/oauth/v2/authorize` with valid prod-consumer params: healthy → `302`, wedged → hang. It works, but:
- It is a **write** — each healthy probe creates an OIDC auth request; Zitadel does **not** auto-clean auth requests, so ~1440/day accumulate in the eventstore on `db-f1-micro`, and the probe loads the projection path that wedges.
- It hardcodes the consumer `client_id` + `redirect_uri`.

Source investigation (zitadel v4.14.0) established:
- `internal/query/project_role.go`: `searchProjectRoles` is read-only and, when `shouldTriggerBulk=true`, calls `projection.ProjectRoleProjection.Trigger(ctx, handler.WithAwaitRunning())` before the SELECT — the same trigger family that wedged on 2026-06-23.
- `internal/api/grpc/project/v2/query.go`: `ListProjectRoles` calls `q.SearchProjectRoles(ctx, true, …)` → triggers on every call, as a pure read.
- Prod check: `POST https://api.liverty-music.app/zitadel.project.v2.ProjectService/ListProjectRoles` returns `401` in ~0.15s unauthenticated → auth is enforced **before** the trigger, so a valid credential is required to reach (and thus detect) the wedge.
- No official escape: no config disables trigger-on-read; `#10103` is open/unfixed; `/debug/healthz` + `/debug/ready` are generic process checks (no projection-health/lag/self-heal). So a probe-based watchdog stays necessary; this change only makes it read-only.

## Goals / Non-Goals

**Goals:**
- Eliminate the probe's eventstore write side-effect (pure read).
- Remove the consumer-client coupling (subsumes the earlier "dedicated probe client" follow-up).
- Preserve detection fidelity (trigger the projection that actually wedges) and all false-restart guards.
- Keep the watchdog a clearly-annotated stopgap until upstream removes the read-projections.

**Non-Goals:**
- Fixing `#10103` (upstream) or right-sizing Cloud SQL (a frequency lever, tracked separately).
- Changing the restart mechanism, the 2-replica posture, or the conservative guards.
- A notification alert (explicitly dropped).

## Decisions

### D1. Probe = read-only `ProjectService/ListProjectRoles` against a static project id
Connect HTTP+JSON: `POST /zitadel.project.v2.ProjectService/ListProjectRoles` with `Authorization: Bearer <PAT>`, `Content-Type: application/json`, body `{"projectId":"<static-id>"}`. Healthy → `200` fast; wedged → hang (curl `--max-time` → HTTP 000). Chosen over alternatives:
- `/oauth/v2/authorize` (current) — **rejected**: write side-effect + consumer-client coupling.
- `GetAuthRequest` (read-only, triggers `AuthRequestProjection`) — **rejected**: needs a live auth-request id (periodic write to mint) + login-client auth; more state than a static project id.
- A no-credential read endpoint — **does not exist**: every wedge-triggering read path is auth-gated (verified `401` before trigger).

The static `projectId` is config (analogous to the old `client_id`); any existing project works (e.g. the ZITADEL project or the app's own project).

### D2. Credential = dedicated least-privilege watchdog machine user + PAT
Provision (Pulumi, zitadel provider) a `MachineUser` (e.g. `watchdog-probe`) granted only what `ListProjectRoles` requires (project/role read on the target project — least privilege; NOT iam-admin), and a `PersonalAccessToken`. Export the token to GSM; sync to the `zitadel` namespace with External Secrets; mount into the CronJob. Rejected:
- Reusing the `login-client` / `iam-admin` PAT — over-privileged and `LoginClientPatPath` is null (not exported), so not readily available.
- An OIDC client-credentials token minted per run — extra token-endpoint round-trip (and itself a write/cache); a long-lived PAT is simpler for a 1/min job.

### D3. Probe-credential failure is fail-safe and must be monitored
An invalid/expired/over-revoked PAT makes `ListProjectRoles` return `401` fast → the watchdog reads "responded quickly" = healthy → it **stops detecting** but never false-restarts. To avoid silently going blind, the PAT SHALL be long-lived (multi-year, like the existing bootstrap PATs) and its expiry tracked; optionally the probe treats a `401`/`403` distinctly (log a loud "watchdog credential invalid" line) so a future log-based check can catch it. (No alerting in this change — logging only.)

### D4. Everything else unchanged
N-of-N in-run hangs, `/debug/healthz`==200 precondition, `concurrencyPolicy: Forbid`, dedicated restart RBAC, 2 replicas, `WATCHDOG_DRY_RUN` toggle, and the `until-upstream-zitadel-10103-fix` annotation all carry over. Ship the new probe in dry-run first, soak, then activate (same rollout discipline as the original).

## Risks / Trade-offs

- **PAT lifecycle (store/rotate/expire)** → Mitigation: long-lived PAT in GSM via ESO; document expiry; fail-safe means an expired PAT degrades to "no detection", not an outage or restart-loop.
- **PAT over-privilege** → Mitigation: dedicated machine user scoped to project-role read only; never reuse iam-admin.
- **Detection-coverage shift** (authorize triggered `AuthRequestProjection`; this triggers `ProjectRoleProjection`) → Mitigation: 2026-06-23 wedged BOTH simultaneously (shared trigger-infra deadlock hypothesis), so `ProjectRoleProjection` is a faithful detector; if a future wedge variant somehow spares ProjectRole, revisit (could probe both).
- **Connect endpoint/JSON contract drift on Zitadel upgrade** → Mitigation: pin the service path in the manifest + runbook; re-verify on major Zitadel bumps (same discipline as the authorize path).
- **Static `projectId` deleted** → Mitigation: use a stable, always-present project (ZITADEL instance project); document it.

## Migration Plan

1. Pulumi: create the watchdog machine user + PAT + GSM secret (no behavior change yet).
2. K8s: add the `ExternalSecret`; rewrite the CronJob probe to `ListProjectRoles` in **dry-run** (`WATCHDOG_DRY_RUN=true`); keep the old authorize env removed.
3. Soak dry-run; confirm healthy → no action and that the probe authenticates (200, not 401).
4. Flip to active; confirm a healthy run still takes no action.
5. Refresh the runbook.

Rollback: revert the CronJob to the authorize probe (previous manifest) or `suspend: true`; the machine user/secret can remain (harmless) or be removed.

## Open Questions

- Which static `projectId` to pin — the ZITADEL instance project vs the consumer app's project? (Pick the most stable / least likely to be deleted.)
- Does the chosen machine user need an explicit project authorization/grant for `ListProjectRoles` to return `200` (vs `403`)? Confirm the minimal role grant during apply.
- Is the prod `api.liverty-music.app` host or the in-cluster Service the better probe target (gateway-path coverage vs fewer moving parts)? Current lean: keep the public host for parity with real traffic, guarded by the `/debug/healthz` precondition.
