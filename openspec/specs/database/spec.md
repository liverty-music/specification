# database Specification

## Purpose

The `database` capability defines the requirements for reliable, scalable, and secure relational storage. It ensures that critical domain data for users, artists, and concerts is persisted in highly available Cloud SQL instances with appropriate encryption and data integrity guarantees.

## Requirements

### Requirement: Schema migrations MUST be applied before serving traffic

The system SHALL ensure that the database schema is up to date before the application begins accepting requests. Migration execution SHALL be performed by the Atlas Kubernetes Operator via `AtlasMigration` CRD, not by the application itself. ArgoCD sync wave ordering SHALL ensure migrations complete before the backend Deployment rolls out.

#### Scenario: Application startup sequence

- **WHEN** ArgoCD syncs the backend namespace
- **THEN** the AtlasMigration resource SHALL be applied first (lower sync wave)
- **AND** the Atlas Operator SHALL apply all pending migrations
- **AND** the backend Deployment SHALL be synced after migrations succeed (higher sync wave)
- **AND** the application SHALL NOT execute any migration logic at startup

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

### Requirement: Application data SHALL reside in a dedicated schema

All application tables SHALL be created in the `app` schema. The backend application SHALL set `search_path=app` in its DSN to route unqualified table references to the `app` schema.

#### Scenario: Schema isolation

- **WHEN** the backend application connects to the database
- **THEN** the DSN SHALL include `search_path=app`
- **AND** all unqualified table references SHALL resolve to the `app` schema
- **AND** no application tables SHALL exist in the `public` schema

### Requirement: Database tables SHALL NOT include metadata timestamp columns

Application tables SHALL NOT include `created_at` or `updated_at` columns for audit purposes. Business-meaningful timestamps (e.g., `minted_at`, `start_at`, `open_at`, `searched_at`, `scheduled_at`, `sent_at`, `used_at`) SHALL be retained.

#### Scenario: Metadata timestamps removed from all tables

- **WHEN** the migration is applied
- **THEN** the following columns SHALL be dropped:
  - `users.created_at`, `users.updated_at`
  - `events.created_at`, `events.updated_at`
  - `venues.created_at`, `venues.updated_at`
  - `artist_official_site.created_at`, `artist_official_site.updated_at`
  - `followed_artists.created_at`
  - `notifications.created_at`, `notifications.updated_at`
- **AND** `schema.sql` SHALL NOT contain `created_at` or `updated_at` in any table definition

#### Scenario: Business timestamps are preserved

- **WHEN** the migration is applied
- **THEN** the following columns SHALL remain unchanged:
  - `tickets.minted_at`
  - `events.start_at`, `events.open_at`
  - `latest_search_logs.searched_at`
  - `nullifiers.used_at`
  - `notifications.scheduled_at`, `notifications.sent_at`
