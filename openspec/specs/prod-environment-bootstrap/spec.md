# prod-environment-bootstrap Specification

## Purpose

Defines requirements for provisioning the `liverty-music-prod` GCP
infrastructure, capturing the irreversible decisions baked in at
cluster creation (regional Autopilot cluster, Dataplane V2 via Autopilot
default, etcd Application-layer Secrets Encryption via Cloud KMS, IP CIDR
plan matching dev) together with the cost-bounded reversible defaults
(Autopilot-managed compute, no Cloud NAT, GMP cost-bounded via disabled
application auto-monitoring, Cloud SQL `db-f1-micro`). The capability
also contracts that prod hosts the same kinds of peripheral GCP
resources as dev (Cloud SQL, Artifact Registry, Service Accounts, Secret
Manager, Cloud DNS, Certificate Manager), and bounds the scope so that
Kubernetes-side workload bootstrap (ArgoCD Applications, per-namespace
overlays) is explicitly deferred to a separate follow-up change.
## Requirements
### Requirement: Prod GKE cluster SHALL be an Autopilot regional cluster in asia-northeast2
The `liverty-music-prod` GCP project SHALL contain exactly one GKE Autopilot regional cluster whose `location` is `asia-northeast2`. The cluster mode (Standard vs Autopilot) is set at creation and cannot be changed without rebuilding the cluster. This change supersedes the prior decision (recorded in the `provision-prod-gcp-resources` change) to use Standard regional; the rationale is that Autopilot is GKE free-tier-eligible (covering the `$72/month` management fee post-dev-retirement) while regional Standard is not, and Autopilot's operational simplicity matches Liverty Music's workload profile (HPA-driven web apps, no privileged DaemonSets).

#### Scenario: Cluster is Autopilot mode
- **WHEN** describing the prod GKE cluster via `gcloud container clusters describe`
- **THEN** the response SHALL include `autopilot.enabled: true`
- **AND** the cluster SHALL NOT have any user-managed `gcp.container.NodePool` resources (Autopilot manages node provisioning internally)

#### Scenario: Cluster is regional
- **WHEN** describing the prod GKE cluster
- **THEN** the `location` field SHALL equal `asia-northeast2`
- **AND** the cluster SHALL show three zone locations (`asia-northeast2-a`, `asia-northeast2-b`, `asia-northeast2-c`)

#### Scenario: Only one cluster exists in prod
- **WHEN** listing GKE clusters in the `liverty-music-prod` project
- **THEN** exactly one cluster SHALL be returned

#### Scenario: Cluster qualifies for GKE free tier
- **WHEN** the prod GKE cluster has been live for a full billing month
- **AND** the `liverty-music-prod` project is the only project in the billing account with a GKE-free-tier-eligible cluster (i.e., dev has been retired or never had a zonal Standard / Autopilot cluster active that month)
- **THEN** the GCP billing line item for `Kubernetes Engine` cluster management fee SHALL be `$0` for that billing period
- **AND** the `$74.40/month` free tier credit SHALL have been applied against the prod cluster's `$72/month` fee

### Requirement: Prod GKE cluster SHALL enable Dataplane V2
The prod GKE cluster SHALL use Dataplane V2 (`datapathProvider: ADVANCED_DATAPATH`) for its networking. On Autopilot, Dataplane V2 is the default and is enabled automatically — explicit configuration is not required, but the behavior is identical to the Standard cluster's prior explicit setting. Dataplane V2 is irreversible after cluster creation per Google Cloud documentation.

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

### Requirement: Prod cluster SHALL NOT enable Confidential GKE Nodes at cluster level
The prod GKE cluster SHALL NOT enable cluster-level Confidential GKE Nodes. On Autopilot, this knob is not user-exposed at the cluster level; Confidential workloads would be requested per-workload via ComputeClasses if/when needed (deferred to a hypothetical blockchain-mainnet-GA future change). The intent of "no cluster-wide Confidential Nodes" is preserved.

#### Scenario: Cluster-level Confidential Nodes is off
- **WHEN** describing the prod GKE cluster
- **THEN** `confidentialNodes.enabled` SHALL NOT be `true`

### Requirement: Prod cluster SHALL bound Google Managed Service for Prometheus (GMP) cost via disabled application auto-monitoring
Because GMP managed collection cannot be disabled on Autopilot clusters running GKE ≥ 1.25 (per [official docs](https://docs.cloud.google.com/stackdriver/docs/managed-prometheus/setup-managed): *"You can't turn off managed collection in GKE Autopilot clusters running GKE version 1.25 or greater"*), the prod cluster SHALL bound GMP ingestion cost by disabling Autopilot's automatic discovery and scraping of application Pods. Cluster-level workload metrics SHALL therefore become opt-in via per-namespace `PodMonitoring` CRDs (deferred to the `prod-k8s-manifests` follow-up). The unavoidable GKE-managed system pipeline (kubelet, cAdvisor, kube-state-metrics) is accepted as the cost floor. Empirical monthly GMP cost target band: `$5-15/month` for an idle / light cluster.

A user-applied `ClusterPodMonitoring` with `metricRelabeling` keep-rules SHALL NOT be relied on for filtering managed-collection system metrics — its relabel rules only apply to metrics that the CR itself scrapes, not to GKE's independent managed-collection pipeline.

#### Scenario: Automatic application monitoring is disabled at the cluster level
- **WHEN** describing the prod cluster's monitoring configuration via `gcloud container clusters describe`
- **THEN** `monitoringConfig.managedPrometheusConfig.autoMonitoringConfig.scope` SHALL be `NONE` or the field SHALL be unset / absent (Autopilot default — equivalent to `NONE` per [GMP auto-monitoring docs](https://docs.cloud.google.com/stackdriver/docs/managed-prometheus/auto-monitoring): *"Automatic application monitoring is OFF by default for both Autopilot and Standard clusters."*)
- **AND** workload metric collection SHALL be opt-in via explicit `PodMonitoring` CRDs only

#### Scenario: GMP managed collection remains enabled
- **WHEN** describing the prod cluster's monitoring configuration via `gcloud container clusters describe`
- **THEN** `monitoringConfig.managedPrometheusConfig.enabled` SHALL be `true`
- **AND** kubelet / cAdvisor / kube-state-metrics scrapes SHALL continue to be ingested into GMP (they are not user-disable-able on Autopilot ≥ 1.25)

#### Scenario: GMP billing stays bounded
- **WHEN** the prod cluster has been live for a full billing month with idle workloads (only system Pods)
- **THEN** the GCP billing line item for "Managed Service for Prometheus samples ingested" for the `liverty-music-prod` project SHALL be no more than `$20` for that billing period

### Requirement: Workload Pods SHALL request Spot scheduling via the `cloud.google.com/gke-spot` label
On Autopilot, Spot vs on-demand scheduling is per-Pod (no node pool). Pods that can tolerate preemption SHALL include the `cloud.google.com/gke-spot: "true"` nodeSelector. Autopilot honors this label and bills the Pod at Spot Pod rates. This continues the labeling convention already enforced for dev workloads.

#### Scenario: Spot-tolerant Pods have the gke-spot label
- **WHEN** rendering any prod overlay manifest for a Pod that can run on Spot compute
- **THEN** the Pod template SHALL include `nodeSelector: { "cloud.google.com/gke-spot": "true" }`

#### Scenario: Autopilot honors the gke-spot label
- **WHEN** a Pod with `cloud.google.com/gke-spot: "true"` is scheduled on the prod cluster
- **THEN** Autopilot SHALL bill the Pod at Spot Pod rates (vCPU + memory at the discounted Spot tier)
- **AND** the Pod SHALL be eligible for preemption with the standard ~25-second notice

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

### Requirement: Prod public DNS SHALL be managed entirely by Cloudflare, with apex A record bound to the shared GKE Gateway static IP
The prod project SHALL NOT provision any public Cloud DNS zone. All prod public DNS records — apex (`liverty-music.app`), `api.liverty-music.app`, `auth.liverty-music.app`, plus ACME DNS-01 challenge CNAMEs and Postmark DKIM/Return-Path records — SHALL live directly in the single Cloudflare-managed zone `liverty-music.app`. The apex SHALL have an A record pointing to the same `api-gateway-static-ip` GlobalAddress that fronts the prod GKE Gateway. The apex SHALL receive a Google-managed TLS certificate via Certificate Manager with the ACME DNS-01 challenge resolved against the Cloudflare zone.

#### Scenario: Cloud DNS hosts no prod public zones
- **WHEN** running `gcloud dns managed-zones list --project liverty-music-prod`
- **THEN** the output SHALL NOT contain any public zone for `liverty-music.app`, `api.liverty-music.app`, or `auth.liverty-music.app`
- **AND** the only zones present SHALL be the private PSC zone(s) (`asia-northeast2.sql.goog`, `private.googleapis.com`) needed for VPC-internal resolution

#### Scenario: Cloudflare zone is authoritative for all prod public hostnames
- **WHEN** running `dig +trace liverty-music.app`, `dig +trace api.liverty-music.app`, or `dig +trace auth.liverty-music.app`
- **THEN** the authoritative answer SHALL come from Cloudflare nameservers
- **AND** each query SHALL return an A record pointing to the prod `api-gateway-static-ip` IPv4 address

#### Scenario: Apex A record exists and is protected
- **WHEN** Pulumi state for the prod stack contains a `cloudflare.DnsRecord` resource with name `liverty-music.app` (`@` in the zone)
- **THEN** the record SHALL be of type `A`
- **AND** SHALL have `content` equal to the prod `api-gateway-static-ip` address
- **AND** SHALL have `proxied: false`
- **AND** SHALL declare `protect: true` in Pulumi resource options

#### Scenario: Apex certificate exists and serves TLS for the apex hostname
- **WHEN** the GKE Gateway in prod terminates HTTPS for `liverty-music.app`
- **THEN** the presented certificate SHALL be a Google-managed Certificate with `managed.domains: ['liverty-music.app']`
- **AND** the cert SHALL be bound to the shared `api-gateway-cert-map` via a `CertificateMapEntry` whose `hostname` is `liverty-music.app`
- **AND** the cert's `DnsAuthorization` ACME DNS-01 CNAME SHALL resolve via the Cloudflare zone (the CNAME record lives in Cloudflare, not Cloud DNS)

#### Scenario: Prod-stack DNS and Certificate Manager resources are Pulumi-protected
- **WHEN** inspecting the Pulumi resource graph for the prod stack
- **THEN** all `cloudflare.DnsRecord` resources for service A records (`liverty-music.app`, `api.liverty-music.app`, `auth.liverty-music.app`) SHALL declare `protect: true`
- **AND** all `gcp.certificatemanager.Certificate` resources (web-app, backend-server, zitadel) SHALL declare `protect: true`
- **AND** all `gcp.certificatemanager.DnsAuthorization` resources SHALL declare `protect: true`
- **AND** all `gcp.certificatemanager.CertificateMapEntry` resources SHALL declare `protect: true`

