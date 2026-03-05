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
2. Extract the latest timestamp from `origin/main`'s `atlas.sum` (last entry's version prefix)
3. If any added file's timestamp ≤ main's latest → out-of-order detected

**Alternative considered**: Parsing `atlas.sum` directly. Rejected because `atlas.sum` on the branch already includes the new files, making comparison harder.

### 3. Auto-fix with `atlas migrate rebase`

**Decision**: When `--fix` is passed and out-of-order files are detected, run `atlas migrate rebase <version>` for each offending file, then update `kustomization.yaml`.

**Flow**:
1. Detect out-of-order files
2. Run `atlas migrate rebase <version> --env local` for each
3. The rebase renames the file and updates `atlas.sum`
4. Update `kustomization.yaml`: replace old filename with new filename in the `configMapGenerator.files` list

### 4. Hook integration

**Decision**: Add a Claude Code hook in `backend/.claude/settings.json` (PostToolUse on Bash when command matches `git rebase`) that runs `scripts/check-migration-drift.sh --fix`.

**Rationale**: This catches the most common scenario (rebasing onto main before push) automatically. The hook only fires when migrations exist on the branch.

## Risks / Trade-offs

- **[Risk] `atlas migrate rebase` changes file content hash** → This is expected. The `atlas.sum` is recalculated, and CI's `atlas migrate validate` will verify integrity.
- **[Risk] Hook runs on every `git rebase`, even non-migration branches** → The script exits quickly (Check 4 is skipped) when no new migration files are detected. Negligible overhead.
- **[Risk] `origin/main` not fetched** → The script should `git fetch origin main` before comparison, or document that the hook assumes a recent fetch. Decision: require the caller to fetch first (the rebase hook already implies `git fetch`).
