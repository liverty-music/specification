# gke-standard-infrastructure Specification

## Purpose

Defines requirements for the dev GKE Standard cluster configuration, including Spot VM node pools and network topology.
## Requirements
### Requirement: Standard zonal GKE cluster for dev
The dev GKE cluster SHALL be a Standard (non-Autopilot) zonal cluster in `asia-northeast2-a` with a Spot VM node pool.

#### Scenario: Cluster type is Standard
- **WHEN** describing the dev GKE cluster
- **THEN** the cluster mode SHALL be Standard (not Autopilot)
- **AND** the cluster location SHALL be `asia-northeast2-a`

#### Scenario: Spot node pool exists
- **WHEN** listing node pools on the dev cluster
- **THEN** a node pool with `spot: true` SHALL exist
- **AND** the machine type SHALL be `e2-medium`
- **AND** autoscaling SHALL be enabled with min 1 and max 2 nodes

### Requirement: Dev cluster nodes SHALL have public external IPs
Nodes in the dev GKE cluster SHALL NOT use private nodes, allowing direct internet egress without Cloud NAT.

#### Scenario: Nodes have external IPs
- **WHEN** running `kubectl get nodes -o wide` on the dev cluster
- **THEN** every node SHALL show a non-empty `EXTERNAL-IP`

#### Scenario: Cloud NAT is absent for dev
- **WHEN** listing Cloud NAT gateways in the dev GCP project
- **THEN** no Cloud NAT gateway SHALL exist for `asia-northeast2`

### Requirement: Standard cluster Spot nodeSelector
All workload pod templates in the dev environment SHALL use the Standard-cluster Spot label `cloud.google.com/gke-spot: "true"` for node scheduling.

#### Scenario: Dev pod scheduled on Spot node
- **WHEN** rendering any dev overlay manifest
- **THEN** the pod template SHALL include nodeSelector `cloud.google.com/gke-spot: "true"`
- **AND** SHALL NOT include `cloud.google.com/compute-class: autopilot-spot`

### Requirement: Shielded GKE Nodes SHALL be enabled on the Spot node pool
The dev cluster node pool SHALL have Shielded GKE Nodes enabled (`shieldedInstanceConfig`), since Standard clusters do not enforce this automatically unlike Autopilot. This is especially important given nodes have public external IPs (`enablePrivateNodes: false`).

#### Scenario: Node pool has shieldedInstanceConfig enabled
- **WHEN** describing the dev GKE node pool configuration
- **THEN** `shieldedInstanceConfig.enableSecureBoot` SHALL be `true`
- **AND** `shieldedInstanceConfig.enableIntegrityMonitoring` SHALL be `true`

### Requirement: Dev cluster SHALL use LEGACY_DATAPATH (kube-proxy/iptables)
The dev GKE cluster SHALL NOT use ADVANCED_DATAPATH (Dataplane V2 / eBPF). The datapath provider SHALL be `LEGACY_DATAPATH`, removing the `anetd` DaemonSet overhead.

#### Scenario: ADVANCED_DATAPATH is absent
- **WHEN** describing the dev GKE cluster network configuration
- **THEN** `datapathProvider` SHALL NOT be `ADVANCED_DATAPATH`
- **AND** no `anetd` DaemonSet SHALL exist in `kube-system`

#### Scenario: kube-proxy DaemonSet is present
- **WHEN** listing DaemonSets in `kube-system` on the dev cluster
- **THEN** a `kube-proxy` DaemonSet SHALL be present

### Requirement: Dev cluster SHALL disable Google Managed Prometheus
The dev GKE cluster SHALL explicitly disable Google Managed Prometheus (GMP), restrict `monitoringConfig.enableComponents` to `SYSTEM_COMPONENTS`, and include both `SYSTEM_COMPONENTS` and `WORKLOADS` in `loggingConfig.enableComponents`. Workload logging is required so log-based alerts (e.g., backend ERROR log alerts, JWT validation error rate, Atlas migration failure, poison queue messages) can fire on real workload events. Monitoring stays system-only because the project has no metric-based workload alerts today, and enabling GMP would add Cloud Monitoring cost without a current consumer.

#### Scenario: GMP is disabled
- **WHEN** describing the dev GKE cluster monitoring configuration
- **THEN** `managedPrometheus.enabled` SHALL be `false`
- **AND** no `gmp-system/collector` DaemonSet SHALL exist

#### Scenario: Logging includes workloads
- **WHEN** describing the dev GKE cluster logging configuration
- **THEN** `loggingConfig.enableComponents` SHALL contain both `SYSTEM_COMPONENTS` and `WORKLOADS`
- **AND** workload pod stdout SHALL appear in Cloud Logging within ~1 minute of emission under `resource.type="k8s_container"` with the pod's namespace, name, and labels propagated as queryable fields

#### Scenario: Monitoring restricted to system components
- **WHEN** describing the dev GKE cluster monitoring configuration
- **THEN** `monitoringConfig.enableComponents` SHALL contain only `SYSTEM_COMPONENTS`

#### Scenario: Log-based alerts read from workload logs
- **WHEN** a backend container emits a `severity=ERROR` log entry whose payload matches an existing log-based metric filter (e.g., `backend_jwt_validation_zitadel_errors`)
- **THEN** the corresponding Cloud Monitoring `AlertPolicy` SHALL evaluate the rate increase within its `alignmentPeriod` and transition to `OPEN` once the threshold and duration are met
- **AND** the configured notification channels SHALL receive a page

### Requirement: Dev cluster Spot node pool boot disk SHALL be 30GB pd-standard
The dev GKE Spot node pool boot disk SHALL be explicitly configured with `diskSizeGb: 30` and `diskType: pd-standard`. The default GKE values (100GB, pd-balanced) SHALL NOT be used. Rationale: the E2 machine series does not support any Hyperdisk variant per GCP documentation, so pd-standard is the cheapest available type, and 30GB is GKE's recommended minimum that comfortably fits the cluster's image cache without triggering DiskPressure evictions.

#### Scenario: Boot disk size is 30GB
- **WHEN** describing the dev Spot node pool `nodeConfig`
- **THEN** `diskSizeGb` SHALL equal `30`

#### Scenario: Boot disk type is pd-standard
- **WHEN** describing the dev Spot node pool `nodeConfig`
- **THEN** `diskType` SHALL equal `"pd-standard"`

#### Scenario: All running spot nodes use the configured disk
- **WHEN** running `gcloud compute disks list` filtered to the spot pool node prefix
- **THEN** every disk SHALL show `SIZE_GB: 30` and `TYPE: pd-standard`

### Requirement: Dev cluster `kube-dns-autoscaler` SHALL set `preventSinglePointFailure: false`
The dev GKE cluster SHALL override the GKE-managed `kube-dns-autoscaler` ConfigMap (in `kube-system`) so that the linear scaling policy declares `preventSinglePointFailure: false`. The remaining linear-policy fields (`coresPerReplica`, `nodesPerReplica`) SHALL retain GKE's defaults of 256 and 16 respectively. Rationale: with the cluster at 6 vCPU / 3 nodes, the cluster-proportional-autoscaler formula computes 1 desired replica; the single-point-of-failure guard is the only reason kube-dns runs at 2 replicas, consuming an additional 270m CPU that prevents the cluster autoscaler from compacting to 2 spot nodes. dev does not require kube-dns HA — `node-local-dns` caching plus client retries cover the rare reschedule gap.

#### Scenario: ConfigMap declares preventSinglePointFailure false
- **WHEN** running `kubectl get configmap kube-dns-autoscaler -n kube-system -o yaml` on the dev cluster
- **THEN** the `data.linear` JSON value SHALL contain `"preventSinglePointFailure":false`

#### Scenario: kube-dns scales to one replica
- **WHEN** running `kubectl get deployment kube-dns -n kube-system` on the dev cluster after the autoscaler has reconciled
- **THEN** the `READY` count SHALL be `1/1`

#### Scenario: Override is reconciled by ArgoCD
- **WHEN** the GKE control plane resets the ConfigMap to its managed default (e.g., during cluster upgrade)
- **THEN** ArgoCD's `core` Application SHALL re-apply the dev override within one sync interval, restoring `preventSinglePointFailure: false`

#### Scenario: Override is dev-only
- **WHEN** comparing rendered manifests for `prod` and `staging` overlays
- **THEN** neither overlay SHALL include a `kube-dns-autoscaler` ConfigMap override
- **AND** the GKE-default `preventSinglePointFailure: true` SHALL apply in those environments

