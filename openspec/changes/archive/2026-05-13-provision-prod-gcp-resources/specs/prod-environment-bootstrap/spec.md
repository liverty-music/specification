## ADDED Requirements

### Requirement: Prod GKE cluster SHALL be a Standard regional cluster in asia-northeast2
The `liverty-music-prod` GCP project SHALL contain exactly one GKE Standard (non-Autopilot) regional cluster whose `location` is `asia-northeast2`. The cluster mode (Standard vs Autopilot) is set at creation and cannot be changed without rebuilding the cluster.

#### Scenario: Cluster is Standard mode
- **WHEN** describing the prod GKE cluster via `gcloud container clusters describe`
- **THEN** the response SHALL NOT include `autopilot.enabled: true`
- **AND** the cluster SHALL have an explicit node pool managed as a separate `gcp.container.NodePool` resource

#### Scenario: Cluster is regional
- **WHEN** describing the prod GKE cluster
- **THEN** the `location` field SHALL equal `asia-northeast2`
- **AND** the cluster SHALL show three zone locations (`asia-northeast2-a`, `asia-northeast2-b`, `asia-northeast2-c`)

#### Scenario: Only one cluster exists in prod
- **WHEN** listing GKE clusters in the `liverty-music-prod` project
- **THEN** exactly one cluster SHALL be returned

### Requirement: Prod cluster nodes SHALL initially run on Spot e2-medium with public IPs
The prod cluster SHALL start with a single Spot `e2-medium` node pool mirroring dev's configuration, with `enablePrivateNodes: false` (no Cloud NAT). Both choices are mutable and are recorded as the cost-first initial state; flipping to private nodes plus on-demand pools is a separate change triggered when real users arrive.

#### Scenario: Initial Spot node pool exists
- **WHEN** listing node pools on the prod cluster
- **THEN** at least one node pool SHALL have `spot: true`
- **AND** its `machineType` SHALL equal `e2-medium`
- **AND** its autoscaling SHALL be configured with `minNodeCount: 1` and `maxNodeCount: 3`

#### Scenario: Boot disk is 30 GB pd-standard
- **WHEN** describing the prod Spot node pool's `nodeConfig`
- **THEN** `diskSizeGb` SHALL equal `30`
- **AND** `diskType` SHALL equal `pd-standard`

#### Scenario: Shielded GKE Nodes are enabled
- **WHEN** describing the prod node pool's `nodeConfig`
- **THEN** `shieldedInstanceConfig.enableSecureBoot` SHALL be `true`
- **AND** `shieldedInstanceConfig.enableIntegrityMonitoring` SHALL be `true`

#### Scenario: Nodes have public IPs
- **WHEN** running `kubectl get nodes -o wide` on the prod cluster
- **THEN** every node SHALL show a non-empty `EXTERNAL-IP`

#### Scenario: No Cloud NAT is provisioned for prod
- **WHEN** listing Cloud NAT gateways in the `liverty-music-prod` project
- **THEN** no Cloud NAT gateway SHALL exist for `asia-northeast2`

### Requirement: Prod cluster SHALL disable Google Managed Prometheus and restrict logging
The prod GKE cluster SHALL set `managedPrometheus.enabled: false`, set `loggingConfig.enableComponents` to `[SYSTEM_COMPONENTS, WORKLOADS]`, and set `monitoringConfig.enableComponents` to `[SYSTEM_COMPONENTS]` only. These cost-first defaults are mutable and will be revisited when real users arrive.

#### Scenario: GMP is disabled
- **WHEN** describing the prod cluster's monitoring configuration
- **THEN** `managedPrometheus.enabled` SHALL be `false`

#### Scenario: Workloads logs are streamed
- **WHEN** describing the prod cluster's logging configuration
- **THEN** `loggingConfig.enableComponents` SHALL contain exactly `SYSTEM_COMPONENTS` and `WORKLOADS`

#### Scenario: Monitoring is restricted to system components
- **WHEN** describing the prod cluster's monitoring configuration
- **THEN** `monitoringConfig.enableComponents` SHALL contain exactly `SYSTEM_COMPONENTS`

### Requirement: Prod DNS SHALL delegate only api. and auth. subdomains to Cloud DNS, leaving the apex on Cloudflare
The prod project SHALL provision a Cloud DNS public zone scoped to GCP-fronted subdomains (`api.liverty-music.app`, `auth.liverty-music.app`). Cloudflare SHALL remain authoritative for the apex `liverty-music.app`. The Pulumi stack SHALL emit Cloudflare NS records that delegate just the named subzones to Cloud DNS, matching the existing dev pattern (`dev.liverty-music.app` subzone delegated from Cloudflare).

#### Scenario: Cloud DNS hosts only the api. and auth. subdomains
- **WHEN** describing the prod Cloud DNS public zones
- **THEN** zones SHALL exist for `api.liverty-music.app` and `auth.liverty-music.app` (or a single zone covering both `api` and `auth` records, matching the dev pattern)
- **AND** no Cloud DNS zone SHALL exist for the apex `liverty-music.app`

#### Scenario: Cloudflare delegates the subdomain zones
- **WHEN** describing Cloudflare DNS records for `liverty-music.app`
- **THEN** NS records SHALL exist delegating `api.liverty-music.app` and `auth.liverty-music.app` to the Cloud DNS nameservers
- **AND** the apex `liverty-music.app` NS records on Cloudflare SHALL NOT be changed by this provisioning

#### Scenario: Cloudflare retains authority for the apex
- **WHEN** querying authoritative nameservers for `liverty-music.app` (apex)
- **THEN** the response SHALL come from Cloudflare nameservers, not Cloud DNS

### Requirement: Prod GCP infrastructure ships without ArgoCD bootstrap (workloads in follow-up change)
This change SHALL provision the prod GCP infrastructure (GKE cluster, KMS, Cloud SQL, Secret Manager, Cloud DNS, Certificate Manager) without authoring the Kubernetes manifests that drive ArgoCD bootstrap (`argocd-apps/prod/`) or the per-namespace prod overlays (`namespaces/<ns>/overlays/prod/`). Those manifests are explicitly out of scope and SHALL be delivered by a separate follow-up OpenSpec change (working title: `prod-k8s-manifests`). The prod cluster SHALL therefore idle (no ArgoCD Applications synced, no workloads running) until that follow-up change lands.

Rationale: bounding this change's blast radius to GCP-side resources keeps the destructive surface (irreversible cluster settings, KMS key) reviewable as a single coherent PR, and lets the k8s-manifest authoring proceed asynchronously once the live cluster is available for `kubectl kustomize` dry-runs against actual cluster API versions.

#### Scenario: GCP infrastructure is fully provisioned without ArgoCD bootstrap
- **WHEN** this change is fully applied (Pulumi up succeeded, all secrets populated)
- **THEN** the prod GKE cluster, KMS keyring/key, Cloud SQL instance, Cloud DNS zones, Certificate Manager resources, and GCP Service Accounts SHALL all exist and be operational
- **AND** `cloud-provisioning/k8s/argocd-apps/prod/` MAY remain unauthored
- **AND** the prod cluster MAY have no ArgoCD Applications synced
- **AND** the prod cluster MAY have no application workloads running

#### Scenario: Follow-up change is tracked separately
- **WHEN** archiving this `provision-prod-gcp-resources` change
- **THEN** a separate OpenSpec change tracking the prod k8s manifests SHALL be filed before any external traffic is routed to the prod cluster
- **AND** that follow-up change SHALL cover `argocd-apps/prod/` authoring, per-namespace `prod/` overlay decisions, and the initial ArgoCD bootstrap procedure
