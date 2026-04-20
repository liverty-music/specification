# Spec: Dev DB Access

## Purpose

Defines how developers and Claude Code agents access the dev Cloud SQL (PSC) instance from a local machine using a Cloud SQL Auth Proxy Pod deployed in GKE.

## Requirements

### Requirement: A Cloud SQL Auth Proxy Deployment SHALL exist in the dev cluster

A standalone Cloud SQL Auth Proxy Deployment SHALL be deployed in the `backend` namespace of the dev GKE cluster to provide an access point for local DB connections.

#### Scenario: Proxy pod is running

- **WHEN** the dev cluster is operational
- **THEN** a Deployment named `cloud-sql-proxy` SHALL exist in the `backend` namespace
- **AND** it SHALL run `gcr.io/cloud-sql-connectors/cloud-sql-proxy:2` with `--psc` and `--auto-iam-authn` flags
- **AND** it SHALL target the instance connection name `liverty-music-dev:asia-northeast2:postgres-osaka`
- **AND** it SHALL use the `backend-app` ServiceAccount for Workload Identity authentication

### Requirement: Local DB access SHALL be established via kubectl port-forward

Developers and Claude Code agents SHALL connect to the dev Cloud SQL instance by forwarding the proxy pod's port to localhost on port `15432`. Using `15432` avoids conflicts with other locally-running PostgreSQL instances on the default port `5432`.

#### Scenario: Agent or developer establishes a local connection

- **WHEN** the user runs `kubectl port-forward deployment/cloud-sql-proxy 15432:5432 -n backend`
- **THEN** `localhost:15432` SHALL be forwarded to the Cloud SQL Auth Proxy Pod on its port `5432`
- **AND** connections to `localhost:15432` SHALL reach the dev Cloud SQL instance via PSC
- **AND** the user SHALL authenticate as `backend-app@liverty-music-dev.iam` (IAM auth, no password)

#### Scenario: Agent connects using psql

- **WHEN** port-forward is active
- **THEN** the agent SHALL connect with: `psql "host=localhost port=15432 user=backend-app@liverty-music-dev.iam dbname=liverty-music sslmode=disable options='-c search_path=app'"`

### Requirement: Dev DB access procedure SHALL be discoverable from backend/AGENTS.md

The connection procedure SHALL be reachable from `backend/AGENTS.md` so that Claude Code agents can find it without manual instruction. To avoid bloating the always-loaded context, the full procedure lives in a separate reference file linked from AGENTS.md.

#### Scenario: Agent receives connection context

- **WHEN** a Claude Code agent loads `backend/AGENTS.md`
- **THEN** the agent SHALL find a "Dev DB Access" section containing:
  - A pointer to `docs/dev-db-access.md`
  - A note that this is dev-only (not for local Docker Compose)
- **AND** `docs/dev-db-access.md` SHALL contain:
  - The `kubectl port-forward` command
  - The `psql` connection string with all connection parameters

### Requirement: Dev DB access SHALL use existing IAM permissions with no new service accounts

The proxy Deployment SHALL reuse the existing `backend-app` Kubernetes ServiceAccount and its Workload Identity binding. No new GCP IAM roles or service accounts SHALL be created for this feature.

#### Scenario: Proxy authenticates with existing Workload Identity

- **WHEN** the proxy pod starts
- **THEN** it SHALL use the `backend-app` KSA with annotation `iam.gke.io/gcp-service-account: backend-app@liverty-music-dev.iam.gserviceaccount.com`
- **AND** it SHALL authenticate to Cloud SQL using the GSA's IAM token
- **AND** no service account key files SHALL be mounted
