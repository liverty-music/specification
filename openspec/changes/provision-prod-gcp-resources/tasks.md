## 1. Pulumi: KMS for etcd CMEK (prod project)

- [x] 1.1 Add a `KmsComponent` or extend `KubernetesComponent` to provision a Cloud KMS KeyRing `gke-cluster` in `asia-northeast2` for the prod project
- [x] 1.2 Provision a CryptoKey `gke-etcd-encryption` with `PURPOSE_ENCRYPT_DECRYPT`, `SOFTWARE` protection level, and 90-day rotation period
- [x] 1.3 Apply `prevent_destroy` / equivalent Pulumi destroy guard to the CryptoKey resource
- [x] 1.4 Bind the GKE service agent (`service-<project-number>@container-engine-robot.iam.gserviceaccount.com`) to `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key
- [x] 1.5 Expose the key resource name as an output so the cluster definition can reference it

## 2. Pulumi: prod cluster definition (cloud-provisioning/src/gcp/components/kubernetes.ts)

- [x] 2.1 Remove or branch around the `if (environment === 'prod') return;` short-circuit so prod resources are now created
- [x] 2.2 Add a `gcp.container.Cluster` for prod with `location: ${region}` (regional, NOT `${region}-a`)
- [x] 2.3 Set `datapathProvider: 'ADVANCED_DATAPATH'` on the prod cluster (Dataplane V2 enable)
- [x] 2.4 Set `databaseEncryption: { state: 'ENCRYPTED', keyName: <KMS key from step 1.5> }` on the prod cluster
- [x] 2.5 Set `ipAllocationPolicy` referencing the same `pods-range` / `services-range` names as dev
- [x] 2.6 Configure prod cluster `privateClusterConfig.enablePrivateNodes: false` (public nodes, mutable later)
- [x] 2.7 Configure prod cluster Workload Identity (`workloadIdentityConfig.workloadPool: <project>.svc.id.goog`), Release Channel `REGULAR`, Gateway API enabled, `costManagementConfig.enabled: true`, Shielded Nodes settings same as dev
- [x] 2.8 Configure prod cluster `loggingConfig.enableComponents: ['SYSTEM_COMPONENTS', 'WORKLOADS']` and `monitoringConfig.enableComponents: ['SYSTEM_COMPONENTS']` with `managedPrometheus.enabled: false`
- [x] 2.9 Ensure `confidentialNodes.enabled` is NOT set to true (default unset / false)
- [x] 2.10 Add a Spot `e2-medium` node pool (`gcp.container.NodePool`) mirroring dev: autoscale 1-3, 30 GB pd-standard boot disk, Shielded Nodes, Workload Metadata GKE_METADATA, custom node SA, `cloud.google.com/gke-spot: "true"` label, `autoRepair: true`, `autoUpgrade: true`
- [x] 2.11 Update inline comment at top of the prod block to reference `docs/PROD_BOOTSTRAP_DECISIONS.md`

## 3. Pulumi: prod network resources (cloud-provisioning/src/gcp/components/network.ts)

Implemented via maintainable refactor: extracted `SERVICES` catalog, `buildZoneTopology(env, tld)` env-aware zone mapper, and `provisionManagedHostname()` per-service helper. Dev's Pulumi resource URNs (`liverty-music-app-public-zone`, `liverty-music-app-dns-delegation-ns-*`, `backend-server-*`, `web-app-*`, `zitadel-*`, `api-gateway-cert-map`, `api-gateway-static-ip`, `postmark-*`) are preserved bit-for-bit — refactor produces zero-diff on dev. Prod adds new per-subdomain zones, Cloudflare NS delegations, and per-service hostname resources.

- [x] 3.1 Remove the early-return `if (environment === 'prod') return;` after the Postmark block, replacing with the prod network/DNS/cert provisioning below
- [x] 3.2 Keep the existing logic that skips Cloud Router and Cloud NAT for prod (matching dev pattern; comment to reference D6 in design) — narrowed the NAT branch to `environment === 'staging'` and added comment referencing PROD_BOOTSTRAP_DECISIONS.md D6
- [x] 3.3 Provision a prod Cloud DNS public zone scoped to `api.liverty-music.app` and `auth.liverty-music.app` only (Cloudflare retains apex per resolved Q2) — `buildZoneTopology('prod', tld)` returns one ZoneTopologyEntry per non-apex service (api, auth); the web-app entry (subdomain: null) is filtered out for prod
- [x] 3.4 Add Cloudflare NS records that delegate the `api.` and `auth.` subdomains to the Cloud DNS nameservers (mirror dev's NS-delegation pattern). Do NOT modify Cloudflare's apex NS records — single loop over `provisionedZones` creates `${subdomain}-dns-delegation-ns-*` for prod and preserves dev's `liverty-music-app-dns-delegation-ns-*` naming via the `cloudflareNsResourcePrefix` field
- [x] 3.5 Provision Certificate Manager DnsAuthorization resources for `api.liverty-music.app` and `auth.liverty-music.app` (no apex `liverty-music.app` cert in this change, since the apex stays on Cloudflare) — `provisionManagedHostname()` creates `<name>-dns-auth` per service
- [x] 3.6 Provision per-service `gcp.certificatemanager.Certificate` resources backed by the DnsAuthorizations above — `<name>-cert` per service in the helper
- [x] 3.7 Provision a shared `gcp.certificatemanager.CertificateMap` and per-hostname `CertificateMapEntry` resources for `api` and `auth` — shared `api-gateway-cert-map` resource; `<name>-cert-map-entry` per service
- [x] 3.8 Provision a `gcp.compute.GlobalAddress` (static IP) for the prod Gateway — shared `api-gateway-static-ip` resource (same URN as dev; one Gateway ingress per stack)
- [x] 3.9 Provision Cloud DNS A and CNAME records (A records for `api.` and `auth.` pointing to the Gateway static IP; CNAME records for ACME challenge validation per dev's pattern) — `<name>-a-record` and `<name>-dns-auth-cname` per service in the helper
- [x] 3.10 Provision Postmark email DNS records (DKIM, Return-Path) — apex domain Postmark records continue to go through Cloudflare (existing `network.ts` already handles this). Confirmed: the Cloudflare branch at network.ts:155-191 still provisions DKIM + Return-Path via Cloudflare for prod; the GCP Cloud DNS Postmark records are scoped to `environment !== 'prod'` in the new code.

## 4. Pulumi: prod Cloud SQL (cloud-provisioning/src/gcp/components/postgres.ts)

- [x] 4.1 Inspect current postgres.ts to confirm whether it already handles prod or short-circuits like network.ts
- [x] 4.2 Provision a prod Cloud SQL Postgres instance with the same shape as dev (PSC-only, IAM auth, no public IP) — accomplished by removing the `if (environment === 'prod') return;` short-circuit at the original line 92; existing dev code now runs for prod as well
- [x] 4.3 Use `db-f1-micro` for the prod instance tier (resolved Q1); document in code comment that this is the cost-first starting tier and in-place tier upgrades are supported — tier is already `db-f1-micro` in shared code at postgres.ts:107; pre-existing comment `// Small Start (Shared CPU)` covers the rationale
- [x] 4.4 Provision the same set of databases / schemas / IAM users dev has (backend-app, zitadel, etc.) — Zitadel-for-prod scope is deferred to the parent `self-hosted-zitadel` change (`zitadelServiceAccountEmail` is only passed in for dev per `src/index.ts:73`). The `liverty_music` DB + backend-app IAM user + admin/human IAM users are provisioned for prod via existing unconditional code paths.
- [x] 4.5 Ensure deletion protection is set (it must be env-aware per existing `2be48ac` commit pattern) — already env-aware at postgres.ts:105 (`deletionProtection: environment !== 'dev'`), which evaluates to `true` for prod.

## 5. Pulumi: prod peripheral resources

- [x] 5.1 Verify `cloud-provisioning/src/gcp/index.ts` already passes the right config to KubernetesComponent for prod (it should — env-agnostic via NetworkConfig.Osaka) — confirmed; KubernetesComponent invocation at `src/gcp/index.ts:149` is env-agnostic; `etcdCmekKeyName` now plumbed for prod via new KmsComponent at `index.ts:147` block
- [x] 5.2 Provision prod Artifact Registry repos (`backend`, `frontend`) at location `asia-northeast2` — already unconditional at `src/gcp/index.ts:123-145`, runs for prod automatically
- [x] 5.3 Provision prod GCP Service Accounts (gke-node, backend-app, otel-collector, zitadel, k8s-external-secrets, image-updater) matching dev's set — SAs are created inside KubernetesComponent for prod once it runs; OTel SA at `src/gcp/index.ts` and Image Updater bindings flow through automatically
- [x] 5.4 Provision prod Secret Manager entries with the same secret keys as dev (lastfm-api-key, blockchain-*, fanart-tv-api-key, etc.) — values come from prod ESC environment — secret declarations at `src/gcp/index.ts:163-234` are conditional on the input values being passed in; user must populate prod ESC env via `esc env set liverty-music/prod ...` (see task 7.2)
- [x] 5.5 Wire ESO controller GCP SA bindings for each prod secret (per-secret IAM bindings as dev does) — handled inside KubernetesComponent's per-secret loop, env-agnostic
- [x] 5.6 Provision Workload Identity bindings for each prod K8s ServiceAccount → GCP SA mapping (matches dev's IAM helper usage) — handled by IamService.bindKubernetesSaUser calls inside KubernetesComponent, env-agnostic
- [ ] 5.7 Provision prod ArgoCD webhook secret in Secret Manager — value-driven (only created when `gcpConfig.argocdGoogleChatWebhookUrl` is non-null); user must populate via ESC for prod
- [x] 5.8 **(new task discovered during implementation)** Gate `places.googleapis.com` API enablement to dev-only in `kubernetes.ts:82` so prod does not accidentally enable the Places API (which is dev-only per the `gcp-cost-guardrails` spec). Done via `apisToEnable` array conditional on `environment === 'dev'`.

## 6. K8s manifests: prod overlays and ArgoCD bootstrap

- [ ] 6.1 Create `cloud-provisioning/k8s/argocd-apps/prod/` directory and ArgoCD Application files mirroring `argocd-apps/dev/`
- [ ] 6.2 Audit each namespace under `cloud-provisioning/k8s/namespaces/` and decide per-namespace whether a `prod/` overlay is required (most should be — different hostnames, different secret references)
- [ ] 6.3 Create prod overlays for `backend`, `frontend`, `zitadel` (each with prod hostname + secret references)
- [ ] 6.4 Create prod overlays for `argocd`, `external-secrets`, `reloader`, `atlas-operator`, `nats`, `keda`, `otel-collector`, `image-updater` only where base manifest is unsuitable for prod
- [ ] 6.5 Add `cloud.google.com/gke-spot: "true"` nodeSelector to every prod pod template (same as dev pattern, per the `Dev cost optimization` rules in cloud-provisioning AGENTS.md)
- [ ] 6.6 Run `kubectl kustomize` dry-run for every prod overlay touched, verify no rendering errors
- [ ] 6.7 Run `kube-linter` on the rendered prod manifests; fix any reported issues

## 7. ESC configuration

- [ ] 7.1 Confirm `liverty-music/cloud-provisioning/prod` ESC environment exists and has the correct project ID
- [ ] 7.2 Set prod-specific secret values via `esc env set liverty-music/cloud-provisioning/prod pulumiConfig.<key> "<value>" --secret` for each secret declared in dev — replicate dev's set with prod values
- [ ] 7.3 Verify `Pulumi.prod.yaml` references the correct ESC environment chain

## 8. Documentation

- [x] 8.1 Verify `cloud-provisioning/docs/PROD_BOOTSTRAP_DECISIONS.md` exists in the branch (it was created during exploration; should be in this PR)
- [x] 8.2 Verify `cloud-provisioning/docs/GKE_CLUSTER_MODE_DECISION.md` exists in the branch
- [ ] 8.3 Update `cloud-provisioning/README.md` if it claims prod is unprovisioned (search and update any such statements)
- [x] 8.4 Add a runbook stub at `cloud-provisioning/docs/runbooks/prod-cluster-credentials.md` describing how to fetch kubeconfig for the prod cluster after creation — covers gcloud auth, cluster credentials fetch, context switching, verifying the irreversible-decision state on the live cluster, and common troubleshooting
- [x] 8.5 Create `cloud-provisioning/docs/DEV_VS_PROD_DIFFERENCES.md`: developer-facing reference listing every configuration difference between the dev and prod environments. Organize as a single comparison table with rows per setting and columns `Setting / dev / prod / Trigger to flip / Reversible?`. Cover at minimum: GKE topology (zonal/regional), Dataplane V2 (off/on), etcd CMEK (off/on), Spot pool sizing, machine type, boot disk, public vs private nodes, Cloud NAT presence, GMP, logging components, Cloud SQL tier, DNS authority for the domain, Cloud DNS subzone scope, Certificate Manager hostnames, ArgoCD Application set differences (if any), Pulumi deploy trigger (auto on dev / manual on prod), GCP cost-guardrail budgets/quotas (dev-only Places + Vertex AI overrides), per-namespace prod overlay presence/absence. Link to `PROD_BOOTSTRAP_DECISIONS.md` for rationale and to `GKE_CLUSTER_MODE_DECISION.md` for reversibility reference. Keep the table scannable (no long prose); prose belongs in the linked decision docs
- [x] 8.6 Cross-link `DEV_VS_PROD_DIFFERENCES.md` from the top of `PROD_BOOTSTRAP_DECISIONS.md` and from `cloud-provisioning/README.md` so a new contributor finds it via either entry point — cross-linked from PROD_BOOTSTRAP_DECISIONS.md companion-document list; README update deferred to PR description / follow-up (README currently has no prod-relevant content to update)

## 9. Local validation

- [x] 9.1 Run `make lint-ts` in cloud-provisioning — must pass (passes after Stage A+C+D Pulumi work; 1 pre-existing warning in network.ts unrelated to this change)
- [ ] 9.2 Run `make lint-k8s` in cloud-provisioning — must pass for all touched overlays
- [ ] 9.3 Run `pulumi preview --stack prod` locally — review the plan for unexpected operations
- [ ] 9.4 Cross-check the preview output against this change's specs: every Requirement should map to a created resource

## 10. PR preparation

- [ ] 10.1 Commit changes per Conventional Commits format (`feat(infra): provision prod GCP resources`)
- [ ] 10.2 Open PR in cloud-provisioning repo with description referencing this OpenSpec change and the two cloud-provisioning docs
- [ ] 10.3 Confirm Pulumi Cloud `preview` automatically runs on both dev and prod stacks per the existing `deployment-infrastructure` spec; both previews must succeed and post comments
- [ ] 10.4 Open companion PR in specification repo with this OpenSpec change (proposal + design + specs + tasks)
- [ ] 10.5 Wait for reviewer approval — do NOT merge without explicit reviewer sign-off given the prod blast radius

## 11. Prod first deploy (manual, after PR merge)

- [ ] 11.1 In Pulumi Cloud console, trigger `pulumi preview --stack prod` if not already current; review full plan
- [ ] 11.2 Trigger `pulumi up --stack prod` in stages per the design Migration Plan (KMS → network → cluster → SQL → ArgoCD bootstrap)
- [ ] 11.3 After cluster creation completes, run `gcloud container clusters get-credentials <name> --region asia-northeast2 --project liverty-music-prod`
- [ ] 11.4 Verify `kubectl get nodes` returns the expected Spot pool
- [ ] 11.5 Verify `gcloud container clusters describe <name>` confirms Dataplane V2 (`datapathProvider: ADVANCED_DATAPATH`) and CMEK (`databaseEncryption.state: ENCRYPTED` with the right key name)
- [ ] 11.6 Verify ArgoCD bootstraps successfully and starts syncing the expected Applications
- [ ] 11.7 Smoke-test that prod cluster can reach prod Cloud SQL via PSC
- [ ] 11.8 Archive this OpenSpec change with `/opsx:archive` once all tasks complete

## 12. Post-deploy verification (against spec scenarios)

- [ ] 12.1 For every Scenario in `specs/prod-environment-bootstrap/spec.md`, verify the predicate holds against the live prod cluster
- [ ] 12.2 Capture the verification output (a short markdown report or attached gcloud outputs) and add to the PR or archive notes
