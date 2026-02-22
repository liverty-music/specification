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

The system SHALL provide a durable, consistent store for relational data.

#### Scenario: Production Deployment

Given the backend service is deployed to production
When it attempts to persist user data
Then the data SHALL be stored in a highly available Cloud SQL instance
And the data SHALL be encrypted at rest

### Requirement: Application data SHALL reside in a dedicated schema

All application tables SHALL be created in the `app` schema. The backend application SHALL set `search_path=app` in its DSN to route unqualified table references to the `app` schema.

#### Scenario: Schema isolation

- **WHEN** the backend application connects to the database
- **THEN** the DSN SHALL include `search_path=app`
- **AND** all unqualified table references SHALL resolve to the `app` schema
- **AND** no application tables SHALL exist in the `public` schema
