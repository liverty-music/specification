## 1. Provision the watchdog credential (Pulumi)

- [ ] 1.1 Add a dedicated `zitadel.MachineUser` (e.g. `watchdog-probe`) in `cloud-provisioning/src/zitadel/…`, least-privilege
- [ ] 1.2 Grant it only the project/role read needed for `ListProjectRoles` on the chosen static project (confirm whether an explicit project authorization/grant is required to get `200` not `403`) — resolves design.md Open Question 2
- [ ] 1.3 Create a `PersonalAccessToken` (long-lived) for that machine user and write the token to a GSM secret (follow the `zitadel-machine-key-for-<principal>` naming convention spirit)
- [ ] 1.4 `pulumi preview` clean; confirm the GSM secret is created and holds a usable PAT

## 2. Sync the PAT into the cluster (External Secrets)

- [ ] 2.1 Add an `ExternalSecret` (prod overlay) that syncs the GSM PAT into a `zitadel`-namespace Secret
- [ ] 2.2 `kustomize build --enable-helm` renders cleanly; confirm the ESO `SecretStore`/refresh wiring matches existing patterns

## 3. Rewrite the watchdog probe (read-only)

- [ ] 3.1 Pick the static `projectId` to probe (stable, always-present — e.g. the ZITADEL instance project); document it inline — resolves design.md Open Question 1
- [ ] 3.2 Rewrite the CronJob script: `POST {host}/zitadel.project.v2.ProjectService/ListProjectRoles` with `Authorization: Bearer $PAT`, `Content-Type: application/json`, body `{"projectId":"…"}`, `--max-time` above normal latency / below gateway timeout; HTTP 000 (hang) = wedge signal; `401`/`403` = log "watchdog credential invalid" and treat as healthy (no restart)
- [ ] 3.3 Mount the PAT secret as an env/file; drop the old `WATCHDOG_AUTHZ_URL` + consumer `client_id`/`redirect_uri`
- [ ] 3.4 Keep all guards unchanged: `/debug/healthz`==200 precondition, 3/3 in-run hangs, `concurrencyPolicy: Forbid`, dedicated restart RBAC, `until-upstream-zitadel-10103-fix` annotation
- [ ] 3.5 Decide probe host (public `api.liverty-music.app` vs in-cluster Service) — resolves design.md Open Question 3
- [ ] 3.6 Ship in **dry-run** (`WATCHDOG_DRY_RUN=true`) first; `make lint-k8s` passes

## 4. Roll out + verify

- [ ] 4.1 PR → merge → ArgoCD sync; confirm the watchdog run authenticates (probe `200`, not `401`) and healthy → no action in dry-run
- [ ] 4.2 Confirm zero auth-request writes from probing (the side-effect is gone) — spot-check the eventstore/auth-request volume vs the old probe
- [ ] 4.3 Flip to active; confirm a healthy run still takes no action
- [ ] 4.4 `make lint-k8s` + `openspec validate zitadel-watchdog-readonly-probe --strict` pass

## 5. Runbook

- [ ] 5.1 Refresh `cloud-provisioning/docs/runbooks/zitadel-hang.md`: self-healing-first flow, the read-only `ListProjectRoles` probe, "verify recovery via an auth-flow probe, NOT `/debug/healthz`", and the new wedge signature (authorize/searchProjectRoles, DB clean, `num_backends` flat)

## 6. Ship + archive

- [ ] 6.1 After prod rollout + verification, archive the change (recovery on a real wedge remains an opportunistic monitoring item, as in the prior change)
