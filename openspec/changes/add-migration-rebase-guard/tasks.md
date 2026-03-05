## 1. Extend check-migration-drift.sh

- [ ] 1.1 Add Check 4: detect out-of-order migration timestamps by comparing new files against `origin/main`'s latest version
- [ ] 1.2 Add `--fix` mode that runs `atlas migrate rebase <version> --env local` for each out-of-order file (re-scanning after each invocation since rebase renames files and rewrites `atlas.sum`)
- [ ] 1.3 Add kustomization.yaml auto-update after rebase (replace old filename with new filename)

## 2. Hook Integration

- [ ] 2.1 Add PostToolUse hook in `backend/.claude/settings.json` to run `scripts/check-migration-drift.sh --fix` after `git rebase origin` commands (pattern excludes `--abort`, `--continue`, interactive rebases)
- [ ] 2.2 Add rebase-state guard in `check-migration-drift.sh` to exit early if `.git/rebase-merge` or `.git/rebase-apply` exists

## 3. CI Integration

- [ ] 3.1 Add ordering check step to `.github/workflows/atlas-ci.yml` that runs `scripts/check-migration-drift.sh` (detect-only, no `--fix`)
