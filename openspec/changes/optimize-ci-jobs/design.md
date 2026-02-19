## Context

Both frontend and backend repos have CI workflows that were added incrementally and lack consistency. Backend is more mature (paths filters, caching, govulncheck) but misses concurrency controls and permissions. Frontend CI was just added and is minimal. The atlas-ci.yml workflow is partially disabled due to Atlas Cloud dependency. benchmark.yml uses a different Postgres version than test.yml.

## Goals / Non-Goals

**Goals:**
- Apply concurrency cancel-in-progress to all workflows in both repos
- Harden all workflow permissions to minimum required
- Add quality gates missing from frontend (typecheck, format check, coverage threshold, security audit)
- Fix atlas-ci.yml to run without Atlas Cloud using local `atlas migrate lint`
- Fix benchmark.yml Postgres version inconsistency
- Add CI success gate jobs for branch protection rules

**Non-Goals:**
- Reusable workflow refactoring for gemini.yml (separate issue)
- Matrix builds (Node.js or Go version matrix)
- Self-hosted runners or cost optimization beyond concurrency

## Decisions

### 1. Concurrency strategy: per-workflow-per-ref cancellation
Use `${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}` as the concurrency group key.
- **Why**: PR runs cancel previous runs on the same PR; branch pushes cancel previous pushes on the same branch. Prevents queue buildup without losing results from different PRs.
- **Alternative considered**: Per-branch only — too coarse, would cancel unrelated PRs sharing a branch name pattern.

### 2. atlas-ci.yml: `atlas migrate lint` without Atlas Cloud
Replace the commented-out `ariga/atlas-action/migrate/lint` (requires cloud) with a direct CLI call:
```yaml
run: atlas migrate lint --dev-url "${{ env.DATABASE_URL }}" --dir "file://internal/infrastructure/database/rdb/migrations/versions" --format "{{ json . }}"
```
Uses the existing `ci` env in `atlas.hcl` (dev URL = service container). No cloud token required.
- **Why**: The `ci` env already defines `dev` and `migration.dir`. The `ariga/setup-atlas@v0` action already installs the CLI.
- **Alternative considered**: Keep TODO comment — provides no value and wastes runner time.

### 3. Frontend coverage threshold
Enforce thresholds via vitest config rather than CLI flags to keep the workflow clean:
- statements: 20%, branches: 70%, functions: 30%, lines: 20%
- These match the values in issue #23 and reflect the current test coverage baseline.

### 4. Permissions per workflow
| Workflow | Required permissions |
|---|---|
| ci.yaml (frontend) | `contents: read`, `pull-requests: write` (for coverage comment) |
| push-image.yaml (frontend) | `contents: read`, `id-token: write` (already set) |
| lint.yml (backend) | `contents: read` |
| test.yml (backend) | `contents: read` |
| benchmark.yml (backend) | `contents: read` |
| atlas-ci.yml (backend) | `contents: read` |
| deploy.yml (backend) | `contents: read`, `id-token: write` (already set) |

### 5. CI success gate job
Add a final `ci-success` job with `needs: [lint, test, ...]` and `if: always()` that fails if any required job failed. Enables single-check branch protection rules.

## Risks / Trade-offs

- **Coverage thresholds may fail on first run** → Set conservatively low (matching issue #23 values); adjust upward over time.
- **`atlas migrate lint` may surface existing migration issues** → Acceptable: surfacing issues is the goal. If existing migrations fail lint, fix them as part of this change.
- **`cancel-in-progress` on deploy.yml** → Could cancel an in-flight deploy on rapid pushes to main. Mitigated by `cancel-in-progress: false` for deploy workflows (only cancel queued, not running).

## Open Questions

- Should `benchmark.yml` results be stored as artifacts or compared against a baseline? (Deferred — out of scope for this change, track separately.)
