## ADDED Requirements

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
