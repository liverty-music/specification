## 1. Fix existing CI failures (issues #133-136)

- [x] 1.1 Fix gofmt failure on `internal/di/provider.go` in backend (#133) — fixed on main
- [x] 1.2 Fix staticcheck SA5011 in `internal/infrastructure/auth/jwt_validator_test.go` in backend (#134) — fixed on main
- [x] 1.3 Fix migration ordering for `latest_search_logs` table in backend (#135) — fixed on main
- [x] 1.4 Fix biome format errors in frontend test files (#136) — fixed on main

## 2. Create Makefiles

- [x] 2.1 Create `backend/Makefile` with targets: `lint`, `fix`, `test`, `test-integration`, `check`
- [x] 2.2 Create `frontend/Makefile` with targets: `lint`, `fix`, `test`, `check`
- [x] 2.3 Create `specification/Makefile` with targets: `lint`, `fix`, `check`
- [x] 2.4 Create `cloud-provisioning/Makefile` with targets: `lint`, `lint-ts`, `lint-k8s`, `fix`, `check`

## 3. Update CI workflows to use Makefile targets

- [x] 3.1 Update `backend/.github/workflows/lint.yml` to call `make lint`
- [x] 3.2 Update `backend/.github/workflows/test.yml` to call `make test-integration`
- [x] 3.3 Update `frontend/.github/workflows/ci.yaml` lint job to call `make lint`
- [x] 3.4 Update `frontend/.github/workflows/ci.yaml` test job to call `make test`
- [x] 3.5 Remove `frontend/.github/workflows/ci.yaml` typecheck job (merged into `make lint`)
- [x] 3.6 Update `specification/.github/workflows/buf-pr-checks.yml` to call `make lint`
- [x] 3.7 Update `cloud-provisioning/.github/workflows/ci.yml` lint job to call `make lint-ts`, remove typecheck job
- [x] 3.8 Update `cloud-provisioning/.github/workflows/lint.yml` to call `make lint-k8s`

## 4. Configure Claude Code PreToolUse hook

- [x] 4.1 Add PreToolUse hook to `backend/.claude/settings.json`
- [x] 4.2 Add PreToolUse hook to `frontend/.claude/settings.json`
- [x] 4.3 Add PreToolUse hook to `specification/.claude/settings.json`
- [x] 4.4 Add PreToolUse hook to `cloud-provisioning/.claude/settings.json`

## 5. Remove code-verifier skill and update docs

- [x] 5.1 Remove `~/.claude/skills/code-verifier/` directory
- [x] 5.2 Update global `~/.claude/CLAUDE.md` to remove code-verifier references and add Makefile-based workflow
- [x] 5.3 Update `backend/AGENTS.md` Development Commands section to use Makefile targets
- [x] 5.4 Update `frontend/AGENTS.md` Development Commands section to use Makefile targets
- [x] 5.5 Update `cloud-provisioning/AGENTS.md` essential-commands to use Makefile targets
