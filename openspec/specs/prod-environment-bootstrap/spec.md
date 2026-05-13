# prod-environment-bootstrap Specification

## Purpose

Defines requirements for provisioning the initial `liverty-music-prod`
GCP infrastructure, capturing the irreversible decisions baked in at
cluster creation (regional Standard cluster, Dataplane V2, etcd
Application-layer Secrets Encryption via Cloud KMS, IP CIDR plan
matching dev) together with the cost-first reversible defaults (Spot
node pool, public nodes, GMP disabled, Cloud SQL `db-f1-micro`). The
capability also contracts that prod hosts the same kinds of
peripheral GCP resources as dev (Cloud SQL, Artifact Registry,
Service Accounts, Secret Manager, Cloud DNS, Certificate Manager),
and bounds the scope so that Kubernetes-side workload bootstrap
(ArgoCD Applications, per-namespace overlays) is explicitly deferred
to a separate follow-up change.

## Requirements

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

### Requirement: Prod GKE cluster SHALL enable Dataplane V2
The prod GKE cluster SHALL be created with `datapathProvider: 'ADVANCED_DATAPATH'`. Dataplane V2 is irreversible after cluster creation per Google Cloud documentation.

#### Scenario: ADVANCED_DATAPATH is set
- **WHEN** describing the prod GKE cluster network configuration
- **THEN** `datapathProvider` SHALL equal `ADVANCED_DATAPATH`

#### Scenario: anetd DaemonSet is present and kube-proxy is unscheduled
- **WHEN** listing DaemonSets in `kube-system` on the prod cluster
- **THEN** an `anetd` DaemonSet SHALL be present
- **AND** the `kube-proxy` DaemonSet — if present as a Dataplane V2 implementation artifact — SHALL have `desiredNumberScheduled: 0` (no nodes match its selector and no Running pods exist)

#### Scenario: NetworkPolicy enforcement is implicitly enabled
- **WHEN** applying a Kubernetes `NetworkPolicy` resource to the prod cluster
- **THEN** the policy SHALL be enforced by Dataplane V2 without requiring `--enable-network-policy` configuration

### Requirement: Prod GKE cluster SHALL encrypt Kubernetes Secrets via Cloud KMS (etcd CMEK)
The prod GKE cluster SHALL be created with `databaseEncryption.state: ENCRYPTED` referencing a Cloud KMS key managed in the `liverty-music-prod` project. This setting is irreversible at cluster creation.

#### Scenario: databaseEncryption is configured
- **WHEN** describing the prod GKE cluster
- **THEN** `databaseEncryption.state` SHALL be one of `ENCRYPTED` (the Pulumi/Terraform input value) or `ALL_OBJECTS_ENCRYPTION_ENABLED` (GCP's steady-state value emitted by `gcloud container clusters describe` after the initial encryption backfill completes)
- **AND** `databaseEncryption.keyName` SHALL match the pattern `projects/liverty-music-prod/locations/asia-northeast2/keyRings/gke-cluster/cryptoKeys/gke-etcd-encryption`

#### Scenario: Stored Kubernetes Secrets are encrypted with the CMEK key
- **WHEN** a new `kind: Secret` is applied to the prod cluster and stored in etcd
- **THEN** the secret payload at rest SHALL be encrypted with the CMEK key
- **AND** every encryption operation SHALL be logged in the `liverty-music-prod` Cloud Logging project

### Requirement: Prod project SHALL host the Cloud KMS keyring and key for etcd CMEK
A Cloud KMS keyring `gke-cluster` SHALL exist in `liverty-music-prod` at location `asia-northeast2`, containing a CryptoKey `gke-etcd-encryption` configured for symmetric encrypt/decrypt with a 90-day automatic rotation period.

#### Scenario: KeyRing exists
- **WHEN** running `gcloud kms keyrings list --project liverty-music-prod --location asia-northeast2`
- **THEN** a keyring named `gke-cluster` SHALL appear in the output

#### Scenario: CryptoKey is configured for ENCRYPT_DECRYPT
- **WHEN** describing the `gke-etcd-encryption` key in the `gke-cluster` keyring
- **THEN** the key purpose SHALL be `ENCRYPT_DECRYPT`
- **AND** the protection level SHALL be `SOFTWARE`
- **AND** the rotation period SHALL be `7776000s` (90 days)

#### Scenario: GKE service agent has encrypt/decrypt permission
- **WHEN** listing IAM policy bindings on the `gke-etcd-encryption` key
- **THEN** the GKE service agent (`service-<project-number>@container-engine-robot.iam.gserviceaccount.com`) SHALL appear with role `roles/cloudkms.cryptoKeyEncrypterDecrypter`

#### Scenario: KMS resources are Pulumi-managed with destroy protection
- **WHEN** inspecting the Pulumi resource graph for the prod stack
- **THEN** the keyring and cryptoKey SHALL appear as managed resources
- **AND** the cryptoKey SHALL declare `prevent_destroy` or equivalent guard to prevent accidental key destruction

### Requirement: Prod GKE cluster SHALL use the same secondary IP CIDR plan as dev
The prod GKE cluster SHALL use `subnetCidr: 10.10.0.0/20`, `podsCidr: 10.20.0.0/16`, `servicesCidr: 10.30.0.0/20`, and `masterCidr: 172.16.0.0/28` as declared in `NetworkConfig.Osaka`. These ranges are reused without modification across dev and prod because GCP project separation isolates the VPCs. The Service secondary range SHALL be sized at `/20` because it cannot be expanded after cluster creation.

#### Scenario: Subnet primary range matches plan
- **WHEN** describing the cluster subnet in the prod VPC
- **THEN** the primary `ipCidrRange` SHALL equal `10.10.0.0/20`

#### Scenario: Pod secondary range matches plan
- **WHEN** describing the cluster subnet's secondary ranges
- **THEN** a range named `pods-range` SHALL exist with `ipCidrRange: 10.20.0.0/16`

#### Scenario: Service secondary range matches plan
- **WHEN** describing the cluster subnet's secondary ranges
- **THEN** a range named `services-range` SHALL exist with `ipCidrRange: 10.30.0.0/20`

#### Scenario: ipAllocationPolicy references the named ranges
- **WHEN** describing the prod cluster's `ipAllocationPolicy`
- **THEN** `clusterSecondaryRangeName` SHALL equal `pods-range`
- **AND** `servicesSecondaryRangeName` SHALL equal `services-range`

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

### Requirement: Prod cluster SHALL NOT enable Confidential GKE Nodes at cluster level
The prod GKE cluster SHALL be created with `confidentialNodes.enabled: false` or with the field unset. Cluster-level Confidential Nodes is irreversible; enabling is deferred to a per-node-pool decision triggered by blockchain mainnet GA.

#### Scenario: Cluster-level Confidential Nodes is off
- **WHEN** describing the prod GKE cluster
- **THEN** `confidentialNodes.enabled` SHALL NOT be `true`

### Requirement: Prod GCP project SHALL host the same peripheral GCP resources as dev
The `liverty-music-prod` project SHALL contain Pulumi-managed resources of the same kinds the `liverty-music-dev` project contains: Cloud SQL Postgres instance (PSC-only, IAM auth), Artifact Registry repositories for backend and frontend, GCP Service Accounts (gke-node, backend-app, otel-collector, zitadel, eso, image-updater), Secret Manager entries for the same secret keys dev declares, and Cloud DNS plus Certificate Manager resources for the prod hostnames. Configuration values (instance tiers, secret values, hostnames) MAY differ from dev, but the resource kinds SHALL match.

#### Scenario: Cloud SQL instance exists
- **WHEN** listing Cloud SQL instances in the `liverty-music-prod` project
- **THEN** a Postgres instance SHALL exist
- **AND** its `settings.ipConfiguration.privateNetwork` SHALL be set or PSC SHALL be configured matching the dev pattern

#### Scenario: Cloud SQL initial tier is db-f1-micro
- **WHEN** describing the prod Cloud SQL instance
- **THEN** its `settings.tier` SHALL equal `db-f1-micro`

#### Scenario: Artifact Registry repositories exist
- **WHEN** listing Artifact Registry repositories in `liverty-music-prod`
- **THEN** repositories named `backend` and `frontend` SHALL exist in location `asia-northeast2`

#### Scenario: Service Accounts mirror dev's set
- **WHEN** listing GCP Service Accounts in `liverty-music-prod`
- **THEN** at minimum the accounts `gke-node`, `backend-app`, `otel-collector`, `zitadel`, `k8s-external-secrets` SHALL exist

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

### Requirement: Initial prod Pulumi deploy SHALL be manual-triggered
The first `pulumi up` for the prod stack after this change is merged SHALL be triggered manually via the Pulumi Cloud console, not via automatic merge-to-main deployment. This requirement aligns with the existing `deployment-infrastructure` capability's "Manual Deployment Flow (Prod)" requirement and is restated here for emphasis given the destructive blast radius of green-field provisioning.

#### Scenario: Prod merge does not auto-deploy
- **WHEN** the cloud-provisioning PR implementing this change is merged to `main`
- **THEN** Pulumi Cloud SHALL NOT automatically trigger `pulumi up` for the prod stack
- **AND** a `pulumi preview` SHALL run automatically for the prod stack
- **AND** the preview SHALL be posted as a PR comment for review

#### Scenario: Operator approves prod up
- **WHEN** an operator reviews the prod preview and approves the deploy
- **THEN** `pulumi up --stack prod` SHALL run via Pulumi Cloud Deployments
- **AND** the resulting GCP resources SHALL match the design's deployment-order plan
