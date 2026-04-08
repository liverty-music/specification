## MODIFIED Requirements

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

## ADDED Requirements

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
The dev GKE cluster SHALL explicitly disable Google Managed Prometheus (GMP) and restrict logging and monitoring to system components only.

#### Scenario: GMP is disabled
- **WHEN** describing the dev GKE cluster monitoring configuration
- **THEN** `managedPrometheus.enabled` SHALL be `false`
- **AND** no `gmp-system/collector` DaemonSet SHALL exist

#### Scenario: Logging restricted to system components
- **WHEN** describing the dev GKE cluster logging configuration
- **THEN** `loggingConfig.enableComponents` SHALL contain only `SYSTEM_COMPONENTS`

#### Scenario: Monitoring restricted to system components
- **WHEN** describing the dev GKE cluster monitoring configuration
- **THEN** `monitoringConfig.enableComponents` SHALL contain only `SYSTEM_COMPONENTS`
