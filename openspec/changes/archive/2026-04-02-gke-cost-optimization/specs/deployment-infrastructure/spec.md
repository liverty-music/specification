## MODIFIED Requirements

### Requirement: All dev workload kinds use Spot VM scheduling
Every workload in the dev environment — including Deployments, StatefulSets, and CronJobs — SHALL include the Spot VM nodeSelector (`cloud.google.com/gke-spot: "true"`).

#### Scenario: CronJob Spot VM coverage
- **WHEN** rendering the backend dev overlay manifests
- **THEN** the concert-discovery CronJob pod template SHALL include nodeSelector `cloud.google.com/gke-spot: "true"`

#### Scenario: All dev workloads on Spot VMs
- **WHEN** running `kubectl get pods -A -o json` on the dev cluster
- **THEN** every pod SHALL be scheduled on nodes with label `cloud.google.com/gke-spot: "true"`
