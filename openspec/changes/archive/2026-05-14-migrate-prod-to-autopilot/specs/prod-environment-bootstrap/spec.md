## MODIFIED Requirements

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
