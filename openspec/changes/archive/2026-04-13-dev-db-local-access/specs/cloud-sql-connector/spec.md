## ADDED Requirements

### Requirement: A standalone Auth Proxy Deployment SHALL exist in dev for local access

In the `development` environment, a standalone Cloud SQL Auth Proxy Deployment SHALL be deployed to provide local DB access without modifying the application's in-process connector.

#### Scenario: Proxy coexists with in-process connector

- **WHEN** the dev cluster is running
- **THEN** the `cloud-sql-proxy` Deployment SHALL exist alongside the backend server Deployment
- **AND** both SHALL connect to the same Cloud SQL instance independently
- **AND** the backend server SHALL continue to use the in-process Go Connector (no change)
- **AND** the proxy Deployment SHALL be deployed only in the `dev` overlay (not staging or production)
