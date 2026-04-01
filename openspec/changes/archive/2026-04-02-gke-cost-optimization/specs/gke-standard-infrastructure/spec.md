## ADDED Requirements

### Requirement: Standard zonal GKE cluster for dev
The dev GKE cluster SHALL be a Standard (non-Autopilot) zonal cluster in `asia-northeast2-a` with a Spot VM node pool.

#### Scenario: Cluster type is Standard
- **WHEN** describing the dev GKE cluster
- **THEN** the cluster mode SHALL be Standard (not Autopilot)
- **AND** the cluster location SHALL be `asia-northeast2-a`

#### Scenario: Spot node pool exists
- **WHEN** listing node pools on the dev cluster
- **THEN** a node pool with `spot: true` SHALL exist
- **AND** the machine type SHALL be `e2-standard-2`
- **AND** autoscaling SHALL be enabled with min 1 and max 4 nodes

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
