## Context

Atlas Operator applies versioned migrations in strict linear order. When parallel branches create migration files with timestamps that predate already-applied migrations on `main`, Atlas rejects them as "non-linear" and stalls indefinitely. This happened on 2026-02-28 and went undetected for a week.

The existing `scripts/check-migration-drift.sh` handles kustomization sync, schema drift, and hash validation, but does not check timestamp ordering. Atlas provides `atlas migrate rebase` to fix ordering issues.

## Goals / Non-Goals

**Goals:**
- Automatically detect out-of-order migration timestamps after `git rebase origin/main`
- Automatically fix ordering via `atlas migrate rebase` when `--fix` is passed
- Automatically update `kustomization.yaml` file references after rebase
- Block PRs in CI when out-of-order migrations are detected
- Integrate into existing `check-migration-drift.sh` as Check 4

**Non-Goals:**
- Changing Atlas Operator configuration (e.g., `exec-order`)
- Handling merge conflicts in migration files (git-level concern)
- Modifying the CI workflow structure beyond adding the new check

## Decisions

### 1. Extend existing script vs. new script

**Decision**: Extend `check-migration-drift.sh` with Check 4.

**Rationale**: The script already handles migration consistency checks and is called from hooks and CI. Adding another check keeps the single entry point. A new script would require separate hook/CI integration.

### 2. Detection method

**Decision**: Compare timestamps of new migration files (files not on `origin/main`) against the latest timestamp on `origin/main`.

**Algorithm**:
1. `git diff --name-only --diff-filter=A origin/main -- k8s/atlas/base/migrations/*.sql` to find added files
2. List migration filenames on `origin/main` and take the lexicographic maximum version prefix as the latest timestamp
3. If any added file's timestamp < main's latest → out-of-order detected

**Alternative considered**: Extracting the latest version from `atlas.sum` (last entry). Rejected because `atlas.sum` uses insertion order, not sorted order — after a prior `atlas migrate rebase` that merged to main, the last entry may not be the highest version.

### 3. Auto-fix with `atlas migrate rebase`

**Decision**: When `--fix` is passed and out-of-order files are detected, run `atlas migrate rebase <version> --env local` where `<version>` is the version prefix of each out-of-order migration file (e.g., `20260227000000` from `20260227000000_add_feature.sql`). Because `atlas migrate rebase` renames the file and rewrites `atlas.sum`, previously collected identifiers become stale after each invocation. The loop must re-scan for out-of-order files after each rebase.

**Flow**:
1. Detect out-of-order files
2. Take the first out-of-order file and extract its version prefix
3. Run `atlas migrate rebase <version> --env local` (this renames the file and updates `atlas.sum`)
4. Update `kustomization.yaml`: replace old filename with new filename in the `configMapGenerator.files` list
5. Re-scan for remaining out-of-order files; repeat from step 2 until none remain

### 4. Hook integration

**Decision**: Add a Claude Code hook in `backend/.claude/settings.json` (PostToolUse on Bash when command matches `git rebase origin`) that runs `scripts/check-migration-drift.sh --fix`.

**Pattern**: The hook pattern is narrowed to `git rebase origin` to avoid firing on `git rebase --abort`, `git rebase --continue`, or interactive rebases. The script also checks for mid-rebase state (`.git/rebase-merge` or `.git/rebase-apply` directory) and exits early if the rebase did not complete successfully.

**Rationale**: This catches the most common scenario (rebasing onto main before push) automatically. The hook only fires when migrations exist on the branch. Running `--fix` during a failed or aborted rebase could corrupt `atlas.sum` and migration files, so the guard is essential.

## Risks / Trade-offs

- **[Risk] `atlas migrate rebase` changes file content hash** → This is expected. The `atlas.sum` is recalculated, and CI's `atlas migrate validate` will verify integrity.
- **[Risk] Hook runs on every `git rebase origin`, even non-migration branches** → The script exits quickly (Check 4 is skipped) when no new migration files are detected. Negligible overhead.
- **[Risk] Hook fires after a failed rebase** → The script checks for `.git/rebase-merge` or `.git/rebase-apply` directories and exits early if the rebase is incomplete. This prevents corrupting migration files during conflict resolution.
- **[Risk] `origin/main` not fetched** → The script should `git fetch origin main` before comparison, or document that the hook assumes a recent fetch. Decision: require the caller to fetch first (the rebase hook already implies `git fetch`).
