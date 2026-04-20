## Why

Multiple projects on the same developer machine run PostgreSQL on the default port `5432`, causing port conflicts that force developers to stop other projects' databases before working on liverty-music. The backend's local Docker Compose `postgres` service and the dev Cloud SQL Auth Proxy `port-forward` both hardcode `5432`, making peaceful coexistence impossible without manual workarounds.

## What Changes

- Move the local Docker Compose `postgres` listen port from `5432` to `15432` (keep `network_mode: host` to preserve the Podman/WSL2 bridge-networking workaround).
- Update `dev-db-access` capability so `kubectl port-forward` and the `psql` reference use `localhost:15432` instead of `localhost:5432`.
- Keep the `DatabaseConfig.Port` default value at `5432` in `backend/pkg/config/config.go` (the default represents the upstream PostgreSQL standard; dev/prod Cloud SQL targets are unchanged).
- Update all local-developer-facing configuration (`.env.test`, `atlas.hcl` env "local", Claude `settings.json` allowlist, integration test setup) to use `15432`.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `dev-db-access`: The `kubectl port-forward` command and `psql` connection example change their localhost port from `5432` to `15432`. No change to the remote side (Cloud SQL still listens on `5432` via PSC).

## Impact

- **Affected repos**: `specification` (spec delta), `backend` (compose, env, atlas config, settings, test setup).
- **Not affected**: `cloud-provisioning` (Cloud SQL / K8s DATABASE_PORT stays `5432`), GitHub Actions service containers, `backend/k8s/atlas/base/atlas-migration.yaml`.
- **Developer action required**: After merging, developers must `docker compose down` and recreate the local `postgres` container; any cached `localhost:5432` bookmarks/scripts pointing to liverty-music's local DB must be updated to `15432`.
- **No data migration**: Port change only; the `postgres_data` volume is preserved.
- **BSR / generated code**: No proto changes.
