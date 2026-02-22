## ADDED Requirements

### Requirement: Dev backend runs single replica

The backend server deployment in the dev environment SHALL run with 1 replica. Production and staging environments retain their default replica count.

#### Scenario: Dev backend replica count

- **WHEN** rendering the backend dev overlay manifests
- **THEN** the server-app Deployment SHALL have replicas set to 1

### Requirement: All dev workload kinds use Spot VM scheduling

Every workload in the dev environment — including Deployments, StatefulSets, and CronJobs — SHALL include the Spot VM nodeSelector (`cloud.google.com/compute-class: autopilot-spot`).

#### Scenario: CronJob Spot VM coverage

- **WHEN** rendering the backend dev overlay manifests
- **THEN** the concert-discovery CronJob pod template SHALL include nodeSelector `cloud.google.com/compute-class: autopilot-spot`

#### Scenario: All dev workloads on Spot VMs

- **WHEN** running `kubectl get pods -A -o json` on the dev cluster
- **THEN** every pod SHALL be scheduled on nodes with compute class `autopilot-spot`
