## MODIFIED Requirements

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

### Requirement: Prod cluster SHALL NOT enable Confidential GKE Nodes at cluster level
The prod GKE cluster SHALL NOT enable cluster-level Confidential GKE Nodes. On Autopilot, this knob is not user-exposed at the cluster level; Confidential workloads would be requested per-workload via ComputeClasses if/when needed (deferred to a hypothetical blockchain-mainnet-GA future change). The intent of "no cluster-wide Confidential Nodes" is preserved.

#### Scenario: Cluster-level Confidential Nodes is off
- **WHEN** describing the prod GKE cluster
- **THEN** `confidentialNodes.enabled` SHALL NOT be `true`

## ADDED Requirements

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

## REMOVED Requirements

### Requirement: Prod cluster nodes SHALL initially run on Spot e2-medium with public IPs
**Reason**: Autopilot manages node provisioning internally — users do not declare `gcp.container.NodePool` resources, machine types, boot disks, or `enablePrivateNodes` toggles. The original requirement's scenarios (`spot: true` on node pool, `machineType: e2-medium`, `diskSizeGb: 30`, `enablePrivateNodes: false`, etc.) are not expressible on Autopilot.

**Migration**: 
- Spot scheduling moves from node-pool level to Pod level via the existing `cloud.google.com/gke-spot: "true"` label (formalized in the new `Workload Pods SHALL request Spot scheduling via the cloud.google.com/gke-spot label` requirement).
- Public-vs-private nodes is no longer user-controlled on Autopilot; the cluster's default network configuration applies. Cloud NAT remains unprovisioned per the original cost-first decision (which still holds — there are no workloads needing egress yet).
- Boot disk type/size are managed by Autopilot. Operators no longer choose between pd-standard, pd-balanced, and Hyperdisk.
- Shielded GKE Nodes are enforced by Autopilot automatically (one of Autopilot's mandatory security defaults).

### Requirement: Prod cluster SHALL disable Google Managed Prometheus and restrict logging
**Reason**: Autopilot ≥ 1.25 cannot disable managed Prometheus collection per [official docs](https://docs.cloud.google.com/stackdriver/docs/managed-prometheus/setup-managed): *"You can't turn off managed collection in GKE Autopilot clusters running GKE version 1.25 or greater"*. The original requirement's first scenario (`managedPrometheus.enabled` SHALL be `false`) cannot be satisfied on Autopilot.

**Migration**: GMP managed collection becomes mandatory; cost is bounded by setting `monitoringConfig.managedPrometheus.autoMonitoringConfig.scope: 'NONE'` at cluster creation to prevent auto-discovery of application Pods. This is formalized in the new `Prod cluster SHALL bound Google Managed Service for Prometheus (GMP) cost via disabled application auto-monitoring` requirement. The empirical cost target is `$5-15/month` (vs the previous `$0` under Standard mode with GMP disabled).

The original logging-component restriction (`loggingConfig.enableComponents` to `[SYSTEM_COMPONENTS, WORKLOADS]`) is also relaxed: Autopilot manages logging configuration internally and exposes fewer knobs. The cluster's default Autopilot logging behavior is accepted.
