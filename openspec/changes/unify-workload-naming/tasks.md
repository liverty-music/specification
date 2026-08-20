> Migration runs **prod-direct** (dev is intentionally stopped for cost). Safety comes
> from the additive create-new → cutover → delete-old discipline, with the new workload
> self-verified in prod while detached before cutover. See design.md D7.

## 1. Convention + tooling

- [x] 1.1 Land the `workload-naming-convention` spec (canonical name mapping table as the source of truth) and the `zitadel-self-hosted-deployment` GSM-key delta via a specification PR → merge (no Release; docs/spec only) — landed on main via merged PR #800; prod-direct design refinement (D7) follows in a small docs PR
- [x] 1.2 Add a rename helper/checklist to cloud-provisioning docs capturing the create-new → cutover → delete-old order per resource class (from design.md)

## 2. fan audience — `web-app`→`fan-web`, `server-app`→`fan-api` (highest blast radius)

### 2a. Identity + infra (cloud-provisioning, additive)
- [x] 2.1 Add GSA `fan-api` with the FULL binding set replicated from `backend-app` (cloudsql.client + cloudsql.instanceUser + logging/monitoring/cloudtrace/aiplatform/serviceusage + artifact-registry reader), WI binding, and per-secret SecretAccessor bindings; keep `backend-app` live — CP PR #408 merged; prod `pulumi up` applied + verified (GSA, 7 roles, WI ns/backend/sa/fan-api, per-secret accessors present)
- [x] 2.2 Add Cloud SQL `CLOUD_IAM_SERVICE_ACCOUNT` user `fan-api@<project>.iam` (postgres.ts); keep `backend-app@…` live — verified `fan-api@…iam` CLOUD_IAM_SERVICE_ACCOUNT on `postgres-osaka`
- [x] 2.3 Zitadel MachineKey: `backend-app` principal ACCEPTED AS NEUTRAL SHARED IDENTITY — event-consumer + 5 cronjobs + fan-api all use the same Zitadel Management API capability; per-workload split is auth-critical large refactor with marginal benefit; `backend-app` machine key retained as the neutral shared credential (same principle as `backend/api` shared image). Accepted non-goal.
- [x] 2.4 Create AR image repos `backend/fan-api` and `frontend/fan-web`; keep old repos live — NOTE: AR repos are shared (`backend`/`frontend`); `<layer>/<stem>` is an image path, not a new AR Repository resource → no Pulumi change; folded into CI push targets (2.5) + overlay `newName` (2.8)

### 2b. Images + DB grants
- [x] 2.5 Point backend CI push target to `backend/fan-api` (+ prod retag map) and frontend CI to `frontend/fan-web`; add both to the `bump-prod-pin` image list — DONE: BE PR #394 (fan-api matrix), BE #396+#397 (api matrix + golangci fix), CP #434+#436+#438 (prep/repoint/route); frontend FE #533 (fan-web CI rename), CP #414 (bump-prod-pin routing). Final image: `backend/api` (audience-neutral shared, successor to server+fan-api), `frontend/fan-web`.
- [x] 2.6 Backend grant migration: grant app-schema privileges to the `fan-api@…` IAM DB user (grant-loop, as in organizer-accounts #390) — BE PR #394 merged; verified in prod (AtlasMigration `lastApplied=20260817010000`, reason=Applied; ArgoCD backend-migrations Synced/Healthy)
- [x] 2.7 Cut backend + frontend releases to populate the new AR repos — DONE: backend v1.35.0 (fan-api), v1.36.0 (api); frontend v1.51.0 (fan-web), v1.52.0 (admin-console-web), v1.53.0 (organizer-console-web). All verified in prod AR.

### 2c. K8s create-new + cutover + delete-old
- [x] 2.8 Add `fan-api` Deployment/Service(`fan-api-svc`)/SA(`fan-api`)/HealthCheckPolicy/configmap(`fan-api-config`)/ExternalSecret(`fan-api-backend-secrets`) and `fan-web` Deployment/Service/route, alongside the old — CP #410 (fan-api), CP #416 (fan-web); both verified 1/1 Ready in prod.
- [x] 2.9 Cutover: repoint `api.liverty-music.app` → `fan-api-svc` and `liverty-music.app` → `fan-web`; verify 200 + DB connect + Zitadel JWT auth — CP #411 (fan-api), CP #417 (fan-web); both verified 200 in prod.
- [x] 2.10 Delete old `server-app`/`web-app` workloads + their configs/secrets — CP #412 (webhook cutover), CP #413 (server delete-old), CP #418 (fan-web delete-old). NOTE: `backend-app` GSA/DBuser KEPT (neutral shared identity, see 2.3). `backend/server` image fully retired via `backend/api` consolidation (backend/api:v1.36.0 in prod, CP #436).

## 3. admin-console — `admin-app`→`admin-console-web` (+ ExternalSecret align)

- [x] 3.1 Rename ExternalSecret `admin-console-secrets`→`admin-console-api-secrets` (new target Secret + deployment mount), create-new → cutover → delete-old — CP #439 (create-new: new ESO, SecretSynced verified in prod), CP #440 (cutover+delete-old: deployment repointed, old ESO pruned, api.admin 200, admin-console-api 1/1 Ready).
- [x] 3.2 Create AR repo `frontend/admin-console-web`, point frontend CI + pin list, release to populate — FE #535 (CI rename), CP #419 (bump-prod-pin + inert pin), FE v1.52.0 (prod AR). NOTE: `frontend/admin-console-web` used directly; `frontend/admin-app` path never created.
- [x] 3.3 Add `admin-console-web` Deployment/Service/route alongside `admin-app`; cutover `admin.liverty-music.app` → `admin-console-web`; verify 200; delete `admin-app` — CP #420 (create-new), CP #421 (cutover), CP #422 (delete-old); prod-verified 200, admin-console-web 1/1 Running.
- [x] 3.4 Confirm `admin-console-api` (already conforming) is unaffected — verified throughout; admin-console-api SA/svc/route all convention-named.

## 4. organizer-console — `organizer-app`→`organizer-console-web`

- [x] 4.1 Create AR repo `frontend/organizer-console-web`, point CI + pin list, release to populate — FE #536 (CI rename), CP #424 (bump-prod-pin + inert pin), FE v1.53.0 (prod AR).
- [x] 4.2 Add `organizer-console-web` Deployment/Service/route alongside `organizer-app`; cutover `organizer.liverty-music.app` → `organizer-console-web`; verify 200; delete `organizer-app` — CP #426 (create-new), CP #427 (cutover, zero-downtime), CP #428 (delete-old); prod-verified 5/5 200, organizer-console-web 1/1 Running.
- [x] 4.3 Confirm the future organizer backend API is planned as `organizer-console-api` in `organizer-rpc-server` (①4/4) — no rename needed there; confirmed out-of-scope.

## 5. event-consumer — `consumer-app`→`event-consumer`

- [x] 5.1 Image strategy decided: reuse existing `backend/consumer` image (no per-workload image, mirrors fan-api/backend/api pattern) — CP #430. NOTE: final image naming consolidated further: `backend/consumer` (neutral tier name) backs `event-consumer` workload.
- [x] 5.2 Rename `consumer-app` → `event-consumer` (Deployment/ScaledObject/configmap), keeping JetStream durable names unchanged; ArgoCD sync — CP #430 (git mv base/consumer→base/event-consumer, all overlay patches retargeted). Verified HPA keda-hpa-event-consumer 19 triggers, 0 restarts, 0 `<unknown>`.
- [x] 5.3 Old `consumer-app` pruned by ArgoCD after rename; durables intact (all 19 HPA triggers resolving), no event backlog confirmed.

## 6. Monitoring + spec reconciliation

- [x] 6.1 Update PodMonitoring, AlertPolicies referencing old workload names — CP #431 (ArgoCD ignoreDifferences consumer-app→event-consumer; deleted vestigial `backend-server` PodMonitoring — was mis-specified since prod bootstrap, 0 series ingested, no AlertPolicy dep); CP #432 (retarget prod alert filters server→fan-api, consumer→event-consumer in monitoring.ts + zitadel-monitoring.ts; prod `pulumi up` applied, Fan API/Event Consumer alerts live).
- [x] 6.2 Spec sweep: reconcile incidental old-name references across main specs — specification PR #816 merged (13 spec files: server-app/consumer-app/web-app, image paths, route/configmap names; DNS/cert Pulumi resource names and backend-app left as accepted non-goals).

## 7. Ship to prod + verify

- [x] 7.1 Prod migration applied audience-by-audience with health verification at each step — fan (2026-08-18), admin-console-web (2026-08-19), organizer-console-web + event-consumer (2026-08-19/20), backend/api consolidation (2026-08-20). All prod-direct with prod pulumi up where needed.
- [x] 7.2 Prod verification: all Deployments convention-named (fan-api+admin-console-api→backend/api:v1.36.0, event-consumer→backend/consumer:v1.36.0, fan-web-app/admin-console-web-app/organizer-console-web-app); all 5 endpoints 200; event-consumer HPA 19 triggers no `<unknown>`; ArgoCD backend+frontend Synced/Healthy.
- [x] 7.3 Cleanup: no old-named GSAs (old: server-app/consumer-app/web-app/admin-app/organizer-app — never existed; fan-api+admin-console-api+backend-app present as designed); no old-named routes (server-admin-route renamed to admin-console-api-route via CP #438); no stale monitoring queries (6.1); no `<unknown>` HPA. DNS record Pulumi resource names (web-app/admin-app/organizer-app/backend-server) = accepted non-goal (aliases cannot avoid prod TLS cert replacement; subdomains unchanged). backend-app neutral shared identity = accepted non-goal.
