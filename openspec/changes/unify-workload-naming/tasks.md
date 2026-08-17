## 1. Convention + tooling

- [ ] 1.1 Land the `workload-naming-convention` spec (canonical name mapping table as the source of truth) and the `zitadel-self-hosted-deployment` GSM-key delta via a specification PR → merge (no Release; docs/spec only)
- [ ] 1.2 Add a rename helper/checklist to cloud-provisioning docs capturing the create-new → cutover → delete-old order per resource class (from design.md)

## 2. fan audience — `web-app`→`fan-web`, `server-app`→`fan-api` (highest blast radius)

### 2a. Identity + infra (cloud-provisioning, additive)
- [ ] 2.1 Add GSA `fan-api` with the FULL binding set replicated from `backend-app` (cloudsql.client + cloudsql.instanceUser + logging/monitoring/cloudtrace/aiplatform/serviceusage + artifact-registry reader), WI binding, and per-secret SecretAccessor bindings; keep `backend-app` live
- [ ] 2.2 Add Cloud SQL `CLOUD_IAM_SERVICE_ACCOUNT` user `fan-api@<project>.iam` (postgres.ts); keep `backend-app@…` live
- [ ] 2.3 Re-issue the Zitadel `backend-app` MachineKey under the `fan-api` principal into GSM `zitadel-machine-key-for-fan-api`; keep the old secret live
- [ ] 2.4 Create AR image repos `backend/fan-api` and `frontend/fan-web`; keep old repos live. `pulumi up` (dev then prod)

### 2b. Images + DB grants
- [ ] 2.5 Point backend CI push target to `backend/fan-api` (+ prod retag map) and frontend CI to `frontend/fan-web`; add both to the `bump-prod-pin` image list
- [ ] 2.6 Backend grant migration: grant app-schema privileges to the `fan-api@…` IAM DB user (grant-loop, as in organizer-accounts #390)
- [ ] 2.7 Cut backend + frontend releases to populate the new AR repos (dual-published)

### 2c. K8s create-new + cutover + delete-old
- [ ] 2.8 Add `fan-api` Deployment/Service(`fan-api-svc`)/SA(`fan-api`)/HTTPRoute(`fan-api-route`)/HealthCheckPolicy(`fan-api-policy`)/configmap(`fan-api-config`)/ExternalSecret(`fan-api-secrets`) and `fan-web` Deployment/Service/route, alongside the old; set fan-api `DATABASE_USER=fan-api@…`; ArgoCD sync
- [ ] 2.9 Cutover: repoint `api.liverty-music.app` → `fan-api-route`/`fan-api-svc` and the fan bundle host → `fan-web`; update the `verify-bundle-isolation` allowlist; verify 200 + DB connect + Zitadel JWT auth + bundle isolation
- [ ] 2.10 Delete old `server-app`/`server-route`/`server-svc`/`web-app` + their configmaps/secrets; then delete `backend-app` GSA, `backend-app@…` DB user, `zitadel-machine-key-for-backend-app`, and old AR repos. `pulumi up`; confirm no dangling refs

## 3. admin-console — `admin-app`→`admin-console-web` (+ ExternalSecret align)

- [ ] 3.1 Rename ExternalSecret `admin-console-secrets`→`admin-console-api-secrets` (new target Secret + deployment mount), create-new → cutover → delete-old
- [ ] 3.2 Create AR repo `frontend/admin-console-web`, point frontend CI + pin list, release to populate
- [ ] 3.3 Add `admin-console-web` Deployment/Service/route alongside `admin-app`; cutover `admin.liverty-music.app` → `admin-console-web`; update bundle-isolation allowlist; verify 200 + isolation; delete `admin-app` + old AR repo
- [ ] 3.4 Confirm `admin-console-api` (already conforming) is unaffected

## 4. organizer-console — `organizer-app`→`organizer-console-web`

- [ ] 4.1 Create AR repo `frontend/organizer-console-web`, point CI + pin list, release to populate
- [ ] 4.2 Add `organizer-console-web` Deployment/Service/route alongside `organizer-app`; cutover `organizer.{base}` → `organizer-console-web`; update bundle-isolation allowlist; verify 200 + isolation; delete `organizer-app` + old AR repo
- [ ] 4.3 Confirm the future organizer backend API is planned as `organizer-console-api` in `organizer-rpc-server` (①4/4) — no rename needed there

## 5. event-consumer — `consumer-app`→`event-consumer`

- [ ] 5.1 Create AR repo `backend/event-consumer` (or reuse the backend image with a renamed Deployment — decide in impl), point CI + pin list
- [ ] 5.2 Add `event-consumer` Deployment/Service/ScaledObject/configmap/PodMonitoring alongside `consumer-app`, keeping the existing JetStream durable names unchanged; ArgoCD sync; verify HPA currentMetrics not `<unknown>` and events consumed
- [ ] 5.3 Delete `consumer-app` + old ScaledObject/configmap/AR repo; confirm durables intact and no event backlog

## 6. Monitoring + spec reconciliation

- [ ] 6.1 Update `app.kubernetes.io/name` labels, PodMonitoring, dashboards, and AlertPolicies referencing old workload names; verify metrics/alerts resolve post-cutover
- [ ] 6.2 Spec sweep: reconcile incidental old-name references against `workload-naming-convention` across `identity-management`, `deployment-infrastructure`, `prod-image-pipeline`, `k8s-resource-right-sizing`, `prod-image-tag-immutability`, `argocd-image-automation`, `frontend-hosting`, `apex-frontend-serving`, `prod-environment-bootstrap`, `zitadel-action-webhook`, `secret-management`, `dev-db-access`, `atlas-operator`, `argocd-*` (specification PR → merge)

## 7. Ship to prod + verify

- [ ] 7.1 Apply each audience's migration to prod (pulumi up prod + releases + prod pin bumps + ArgoCD sync), audience-by-audience with health verification between cutovers
- [ ] 7.2 Prod verification: all workloads render under the new names (`kubectl get deploy` shows only convention names); `api.liverty-music.app` / `admin.liverty-music.app` / `organizer.{base}` all 200; fan-api DB + Zitadel auth OK; event-consumer draining; ArgoCD apps Synced/Healthy
- [ ] 7.3 Cleanup: confirm no old-named GSAs, DB users, GSM secrets, AR repos, routes, or Deployments remain in dev or prod; no `<unknown>` HPA metrics; no stale monitoring queries
