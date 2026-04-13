## Why

Cloud SQL is configured with PSC-only connectivity (no public IP), so developers and Claude Code agents cannot connect to the dev environment database from a local machine. This blocks tasks like ad-hoc queries, schema validation, and debugging data issues that require direct DB access.

## What Changes

- Deploy a `cloud-sql-proxy` Deployment to the dev GKE cluster (namespace: `tools`) that exposes the Cloud SQL PSC instance over `kubectl port-forward`
- Add a `dev-db-access` capability spec defining the access pattern and IAM requirements
- Update `backend/AGENTS.md` with the connection procedure so Claude Code agents receive it in context
- Update the `go-postgres` skill with a "Dev DB Access" section covering the port-forward workflow

## Capabilities

### New Capabilities

- `dev-db-access`: Developer and agent access to the dev Cloud SQL (PSC) instance via Cloud SQL Auth Proxy Pod + `kubectl port-forward`

### Modified Capabilities

- `cloud-sql-connector`: Add requirement that a standalone Auth Proxy deployment SHALL exist in dev for local access

## Impact

- **cloud-provisioning**: New K8s Deployment manifest (`k8s/namespaces/tools/`) for the proxy pod; uses existing `backend-app` Workload Identity SA
- **backend AGENTS.md**: New section documenting the `kubectl port-forward` procedure
- **go-postgres skill**: New "Dev DB Access" section with connection steps and caveats
- No application code changes required
- No new GCP IAM roles or service accounts required (reuses `backend-app` SA)
