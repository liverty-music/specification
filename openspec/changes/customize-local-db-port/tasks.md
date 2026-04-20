## 1. Specification repo — spec delta

- [x] 1.1 Run `openspec validate customize-local-db-port --strict` and fix any issues
- [x] 1.2 Commit spec delta on branch `customize-local-db-port`
- [ ] 1.3 Open PR to `specification/main`, wait for `buf-pr-checks.yml` to pass
- [ ] 1.4 Merge PR

## 2. Backend repo — local Docker Compose postgres listen port

- [ ] 2.1 Add `command: ["postgres", "-p", "15432"]` to the `postgres` service in `backend/compose.yml`
- [ ] 2.2 Update the `postgres` healthcheck in `backend/compose.yml` to `pg_isready -U test-user -d test-db -p 15432`
- [ ] 2.3 Recreate the container locally: `docker compose down postgres` then `docker compose up -d postgres --wait`
- [ ] 2.4 Verify connectivity: `psql -h localhost -p 15432 -U test-user -d test-db -c 'SELECT 1'` succeeds

## 3. Backend repo — developer-facing configuration

- [ ] 3.1 Change `DATABASE_PORT=5432` to `DATABASE_PORT=15432` in `backend/.env.test`
- [ ] 3.2 Update the `env "local"` block in `backend/atlas.hcl` so `url` uses `localhost:15432`
- [ ] 3.3 Replace `localhost:5432` with `localhost:15432` in all three atlas allowlist entries in `backend/.claude/settings.json`
- [ ] 3.4 Change `Port: 5432` to `Port: 15432` in `backend/internal/infrastructure/database/rdb/setup_test.go:41`
- [ ] 3.5 Update `backend/.github/workflows/test.yml`: change both postgres service port mappings to `15432:5432` and both `atlas migrate apply` URLs to `localhost:15432`
- [ ] 3.6 Update `backend/.github/workflows/atlas-ci.yml`: change the postgres service port mapping to `15432:5432` and the `DATABASE_URL` env to `localhost:15432`

## 4. Backend repo — verification

- [ ] 4.1 Run `atlas migrate apply --env local` and confirm migrations apply against the new port
- [ ] 4.2 Run `make test` and confirm all unit tests pass
- [ ] 4.3 Run `make check` and confirm no regressions

## 5. Backend repo — commit and PR

- [ ] 5.1 Commit on branch `customize-local-db-port` with a conventional commit message
- [ ] 5.2 Open PR referencing the specification PR (or the merged spec commit if already merged)
- [ ] 5.3 Merge after CI passes

## 6. Post-merge verification

- [ ] 6.1 Confirm `docker compose up -d postgres --wait` succeeds from a clean `git pull` in another worktree
- [ ] 6.2 Confirm dev Cloud SQL access: `kubectl port-forward deployment/cloud-sql-proxy 15432:5432 -n backend` works and the updated `psql` command from the spec delta connects successfully
- [ ] 6.3 Archive the OpenSpec change via `/opsx:archive`
