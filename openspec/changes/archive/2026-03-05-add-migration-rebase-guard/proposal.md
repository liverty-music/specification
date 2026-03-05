## Why

Parallel development branches frequently create migration files with timestamps that conflict when merged in different order than their timestamps suggest. This caused Atlas Operator to stall for a week (2026-02-28 to 2026-03-05) with a non-linear error, blocking all pending migrations on the dev DB. We need automated prevention and detection to avoid recurrence.

## What Changes

- Extend `scripts/check-migration-drift.sh` with a new check that detects out-of-order migration timestamps relative to `origin/main`
- Add `--fix` mode that automatically runs `atlas migrate rebase` and updates `kustomization.yaml` when out-of-order files are detected
- Add a Claude Code hook (PostToolUse: git rebase) in the backend repo to run the script automatically after rebasing onto main

## Capabilities

### New Capabilities

- `migration-rebase-guard`: Automated detection and correction of out-of-order Atlas migration timestamps caused by parallel branch development

### Modified Capabilities

- `database-migration`: Add migration rebase guard to the development workflow and CI pipeline

## Impact

- `backend/scripts/check-migration-drift.sh`: Extended with Check 4 (timestamp ordering) and `--fix` mode
- `backend/.claude/hooks/` or `backend/.claude/settings.json`: New hook for post-rebase migration check
- `backend/.github/workflows/atlas-ci.yml`: CI runs the ordering check on PRs (detect-only mode)
- Development workflow: Developers no longer need to manually detect/fix migration ordering issues
