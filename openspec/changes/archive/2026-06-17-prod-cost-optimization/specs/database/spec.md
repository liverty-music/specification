## MODIFIED Requirements

### Requirement: The system MUST provide persistent relational storage

The system SHALL provide a durable, consistent store for relational data. The Cloud SQL availability tier for each environment SHALL be selected based on the environment's SLA phase: `ZONAL` during the launch phase (cost-priority, single-zone primary, automated daily backups), `REGIONAL` during the steady-state phase (HA with zonal failover). The availability tier SHALL be controlled by Pulumi configuration so that switching between phases is a single PR + `pulumi up` operation.

#### Scenario: Production Deployment

- **WHEN** the backend service is deployed to production during the launch phase
- **THEN** it SHALL persist user data in a Cloud SQL instance with `availabilityType: ZONAL`
- **AND** the data SHALL be encrypted at rest
- **AND** automated daily backups SHALL be retained for the configured retention period

#### Scenario: Promotion to steady-state HA

- **WHEN** an operator decides to promote prod to the steady-state phase
- **THEN** a Pulumi config flag SHALL be flipped to switch `availabilityType` to `REGIONAL`
- **AND** `pulumi up` SHALL trigger the Cloud SQL instance to add a zonal standby
- **AND** the change SHALL be revertible by flipping the flag back

#### Scenario: Failover semantics in ZONAL phase

- **WHEN** the primary Cloud SQL zone experiences an outage during the launch phase
- **THEN** the system SHALL fail to serve database-dependent traffic until manual recovery
- **AND** operators SHALL accept this risk in exchange for ~50% cost savings versus REGIONAL
- **AND** the runbook SHALL document the manual recovery procedure (point-in-time restore from backup)
