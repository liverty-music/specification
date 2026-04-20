## MODIFIED Requirements

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
