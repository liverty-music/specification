## MODIFIED Requirements

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
