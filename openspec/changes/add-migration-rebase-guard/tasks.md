## 1. Extend check-migration-drift.sh

- [ ] 1.1 Add Check 4: detect out-of-order migration timestamps by comparing new files against `origin/main`'s latest version
- [ ] 1.2 Add `--fix` mode that runs `atlas migrate rebase` for each out-of-order file
- [ ] 1.3 Add kustomization.yaml auto-update after rebase (replace old filename with new filename)

## 2. Hook Integration

- [ ] 2.1 Add PostToolUse hook in `backend/.claude/settings.json` to run `scripts/check-migration-drift.sh --fix` after `git rebase` commands

## 3. CI Integration

- [ ] 3.1 Add ordering check step to `.github/workflows/atlas-ci.yml` that runs `scripts/check-migration-drift.sh` (detect-only, no `--fix`)
