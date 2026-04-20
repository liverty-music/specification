## Context

The backend's local development loop depends on a Docker Compose `postgres` service that binds to the host's port `5432`. Because it uses `network_mode: host` (introduced in commit `1faa575` on 2026-02-20 as a workaround for a Podman 5 + netavark + WSL2 bridge-networking bug), Docker port mapping (`ports: "X:5432"`) is not a viable escape hatch — the container grabs whichever host port the PostgreSQL process inside it listens on.

Separately, the `dev-db-access` capability (archive `2026-04-13-dev-db-local-access`) instructs developers and Claude Code agents to run `kubectl port-forward deployment/cloud-sql-proxy 5432:5432` and connect via `localhost:5432`, which collides with any other project's local PostgreSQL on the same machine.

Developers frequently work on multiple projects that each run a default-port PostgreSQL. Today this forces a "stop the other project's DB first" workflow. The goal is to let liverty-music coexist with other local PostgreSQL instances on `5432` without manual intervention.

## Goals / Non-Goals

**Goals:**
- Move both liverty-music local-DB access paths (Docker Compose `postgres`, and `kubectl port-forward` to dev Cloud SQL) off port `5432` onto `15432`.
- Preserve the Podman/WSL2 host-networking workaround (no regression to the original bridge-networking bug).
- Keep the `DatabaseConfig.Port` default value at `5432` (matches upstream PostgreSQL convention and dev/prod Cloud SQL reality).
- Keep the developer-facing ergonomics: `make test`, `atlas migrate apply --env local`, `docker compose up -d postgres` must continue to "just work" after the change.

**Non-Goals:**
- Changing dev/prod Cloud SQL instance ports (they stay at `5432`; only the local `port-forward` LHS changes).
- Changing GitHub Actions service-container ports (`5432:5432` in workflow files — these are isolated CI environments and free of local conflicts).
- Introducing per-developer port customization (single fixed port `15432` for the whole project).
- Revisiting the `network_mode: host` decision.

## Decisions

### Decision 1: Keep `network_mode: host`, change the PostgreSQL listen port via `-p` flag

**Chosen**: Keep `network_mode: host` in `compose.yml` and pass `command: ["postgres", "-p", "15432"]` (and update the `pg_isready` healthcheck with `-p 15432`).

**Alternative considered**: Remove `network_mode: host` and use port mapping `ports: "15432:5432"`.

**Rationale**: Commit `1faa575` adopted host networking specifically because Podman 5 + netavark on WSL2 fails to forward bridge-network ports to the host, making `localhost:X` unreachable. Reverting to bridge networking would reintroduce that bug for affected developers. Changing the postgres listen port keeps the workaround intact while solving the conflict.

### Decision 2: Port number — `15432` (1-prefix convention)

**Chosen**: `15432`.

**Alternative considered**: `54322` (second-postgres convention), `55432` (project-specific extension).

**Rationale**: The 1-prefix convention (`15432`) is widely used in Docker tutorials and PostgreSQL documentation for "an alternate PostgreSQL instance", is easy to remember, and is unambiguous. `54322` is often already consumed by other projects following the same "second-instance" pattern.

### Decision 3: Align the dev Cloud SQL `port-forward` LHS to the same `15432`

**Chosen**: The `dev-db-access` spec prescribes `kubectl port-forward deployment/cloud-sql-proxy 15432:5432` and `psql "... port=15432 ..."`.

**Alternative considered**: Use a different port for dev port-forward (e.g., `15433`) to allow running local compose and dev port-forward simultaneously.

**Rationale**: Local compose and dev port-forward are mutually exclusive by design (the capability is explicitly "dev-only, not for local Docker Compose"). Using a single non-default port `15432` minimises what developers must memorise and keeps config uniform.

### Decision 4: Keep `DatabaseConfig.Port` default at `5432`

**Chosen**: Do not modify the `default:"5432"` tag on `DatabaseConfig.Port` in `backend/pkg/config/config.go`.

**Alternative considered**: Change the default to `15432`.

**Rationale**: `5432` is the upstream PostgreSQL standard and matches dev/prod Cloud SQL. The default represents "when nothing is specified, assume standard PostgreSQL." Local-only port variance is expressed through `.env.test`, not through the code default. Changing the default risks silent production breakage if a deployment ever omits `DATABASE_PORT`.

### Decision 5: Update `setup_test.go` alongside the environment config

**Chosen**: Change the hardcoded `Port: 5432` in `internal/infrastructure/database/rdb/setup_test.go:41` to `15432`.

**Rationale**: Integration tests run on the host against the local `postgres` container (started via `docker compose up -d postgres --wait`). Without updating this constant, `make test` would fail after the port change. A follow-up refactor to source the port from env is out of scope.

## Risks / Trade-offs

- **Risk**: Developers with existing `compose.yml` state may have a `postgres` container still listening on `5432` after `git pull`. → **Mitigation**: Document in the tasks that developers must run `docker compose down postgres` and `docker compose up -d postgres` once after pulling; persistent volume `postgres_data` is not affected.
- **Risk**: Claude Code's `.claude/settings.json` allowlist contains literal `localhost:5432` strings for Atlas commands. Stale allowlist entries trigger permission prompts for previously-approved commands. → **Mitigation**: Update all three literal entries in the same change.
- **Risk**: Any developer-local scripts, `.pgpass`, psql bookmarks, or IDE DB connections pointing at `localhost:5432` (for liverty-music) will break silently. → **Mitigation**: Call out in proposal's "Impact" section and in the backend PR description.
- **Trade-off**: The `DatabaseConfig.Port` default (`5432`) now diverges from the local reality (`15432`). A developer who forgets to source `.env.test` locally would fail to connect — but `.env.test` is checked into the repo and used by all tooling, so this scenario is unlikely.

## Migration Plan

1. Merge `specification` PR first (spec delta for `dev-db-access`).
2. Merge `backend` PR; it covers `compose.yml`, `.env.test`, `atlas.hcl`, `.claude/settings.json`, and `setup_test.go`.
3. Post-merge, each developer:
   - `docker compose down postgres`
   - `git pull`
   - `docker compose up -d postgres --wait`
   - Verify `psql "host=localhost port=15432 ..."` succeeds.
4. For dev Cloud SQL access, developers now use `kubectl port-forward deployment/cloud-sql-proxy 15432:5432 -n backend`.

**Rollback**: Revert both PRs. The `postgres_data` volume is compatible with either port (port is a server runtime flag, not stored in data).

## Open Questions

- None. All technical decisions are resolved.
