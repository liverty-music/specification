## Context

Each repo (backend, frontend, specification, cloud-provisioning) has its own CI workflows with inline commands for linting, formatting, and testing. The AI agent uses a `code-verifier` skill that attempts to replicate these checks locally, but the commands are scattered across AGENTS.md prose and the skill has to infer what to run per repo. This has led to repeated CI failures where checks were skipped or wrong commands were used (issues #133-136).

The specification repo already has `.pre-commit-config.yaml` with buf lint/format hooks. Backend and frontend have no local pre-commit mechanism.

## Goals / Non-Goals

**Goals:**

- Single `make check` command per repo that runs all checks CI would run
- Structural enforcement: AI cannot commit without passing `make check`
- CI workflows reuse the same Makefile targets, eliminating drift between local and CI
- `make fix` for auto-fixing formatting issues
- Separate `make test` (unit, local DB via docker compose) from `make test-integration` (integration, DB provided externally by CI)

**Non-Goals:**

- Changing what is checked (no new lint rules or test requirements)
- E2E / Playwright tests in pre-commit (too slow)
- `govulncheck` / `npm audit` in local checks (CI-only, too slow)
- git pre-commit hooks for human developers (AI-only enforcement for now)

## Decisions

### 1. Makefile as the unified interface

**Decision**: Use GNU Make (Makefile) in each repo with standardized targets.

**Alternatives considered**:
- `npm scripts` + `go task`: Each ecosystem has its own tool, defeating the purpose of unification
- [Taskfile](https://taskfile.dev/): YAML-based, cross-platform, but adds an external dependency
- Shell scripts: No dependency management, no target-level caching

**Rationale**: Make is universally available (including WSL2), has zero dependencies, and is the simplest option. All developers use WSL2, so Windows compatibility is not a concern.

**Standard targets across all repos**:

| Target | Purpose | Local | CI |
|--------|---------|-------|----|
| `lint` | Format check + linter + type check | Yes | Yes (`make lint`) |
| `fix` | Auto-fix formatting | Yes | No |
| `test` | Unit tests (with local DB setup) | Yes | No |
| `test-integration` | Integration tests (DB already running) | No | Yes (`make test-integration`) |
| `check` | `lint` + `test` | Yes | No |

### 2. Claude Code PreToolUse hook replaces code-verifier skill

**Decision**: Add a `PreToolUse` hook in each repo's `.claude/settings.json` that intercepts `git commit` and runs `make check` first. Remove the `code-verifier` skill.

**Alternatives considered**:
- Keep code-verifier skill: It's a prompt-based instruction that the AI can ignore (proven by issues #133-136)
- git pre-commit hook: Would work for human developers too, but adds setup friction and doesn't apply to GitHub Actions Claude agent

**Rationale**: A hook is structural — the AI cannot bypass it. The code-verifier skill relies on the AI choosing to invoke it, which is the exact failure mode we're fixing.

### 3. CI calls Makefile targets

**Decision**: CI workflows call `make lint` and `make test-integration` instead of inline commands.

CI-specific setup (service containers, atlas setup, codecov upload) remains in the workflow YAML. Only the actual check/test commands move to Make.

```
CI workflow structure:
  1. Setup (checkout, language setup, npm ci, DB service)  ← CI-specific
  2. make lint / make test-integration                      ← Shared via Makefile
  3. Post-processing (codecov, vulnerability scan)          ← CI-specific
```

### 4. Backend test/test-integration split

**Decision**:
- `make test`: Starts PostgreSQL via `docker compose`, runs `atlas migrate apply`, then `go test ./...` (unit tests only, no `-tags=integration`)
- `make test-integration`: Runs `go test -tags=integration -race -timeout=5m ./...` assuming DB is already available (CI service container)

**Rationale**: Integration tests are slow and require specific DB state. Local developers run unit tests for fast feedback. CI runs the full integration suite.

### 5. Frontend lint includes all CI checks

**Decision**: `make lint` runs biome lint + biome format check + stylelint + tsc typecheck. This matches CI exactly, preventing the issue #136 pattern where format checking was missing locally.

### 6. Cloud-provisioning split lint targets

**Decision**: Cloud-provisioning has two distinct lint domains — `lint-ts` (biome + tsc) and `lint-k8s` (kustomize render + kube-linter + spot nodeSelector check). `make lint` runs both, but `make check` only runs `lint-ts`.

**Rationale**: `lint-k8s` requires kustomize, kube-linter, and helm installed — tools not available in the standard developer environment. CI installs these tools explicitly. `lint-ts` is sufficient for local pre-commit checks since TypeScript changes are the primary risk area for AI-generated code.

## Risks / Trade-offs

- **`make test` starts docker compose every time** → Mitigation: `docker compose up -d --wait` is idempotent and fast if container already running
- **Hook blocks commit even for non-code changes (docs, config)** → Acceptable: `make check` is fast enough. Can add path-based skip logic later if needed
- **Removing code-verifier skill loses migration drift check** → Accepted trade-off: The backend's `.claude/settings.json` already has a `Write|Edit` PreToolUse prompt hook that warns when migration files are directly edited, recommending `atlas migrate diff` via the `/db-migration` skill. This provides sufficient protection without adding migration drift detection to `make check`
