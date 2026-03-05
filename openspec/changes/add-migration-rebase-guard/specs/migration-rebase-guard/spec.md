## ADDED Requirements

### Requirement: The system MUST detect out-of-order migration timestamps

The migration drift check script SHALL compare timestamps of newly added migration files against the latest migration version on `origin/main`. A file is out-of-order if its timestamp is less than or equal to the latest version on main.

#### Scenario: Branch adds migration with older timestamp than main's latest

- **WHEN** a branch adds `20260227000000_add_feature.sql` but main's latest is `20260227090313`
- **THEN** the script SHALL report `20260227000000_add_feature.sql` as out-of-order
- **AND** the script SHALL exit with non-zero status in detect-only mode

#### Scenario: Branch adds migration with newer timestamp than main's latest

- **WHEN** a branch adds `20260305120000_add_feature.sql` and main's latest is `20260304014803`
- **THEN** the script SHALL report no ordering issues
- **AND** the script SHALL exit with zero status

#### Scenario: No new migration files on branch

- **WHEN** a branch has no new migration files compared to `origin/main`
- **THEN** the ordering check SHALL be skipped silently

### Requirement: The system MUST auto-fix out-of-order migrations when --fix is passed

When invoked with `--fix`, the script SHALL automatically rebase out-of-order migration files using `atlas migrate rebase` and update `kustomization.yaml` references.

#### Scenario: Auto-fix renames and updates kustomization

- **WHEN** `--fix` is passed and out-of-order files are detected
- **THEN** the script SHALL run `atlas migrate rebase <version> --env local` where `<version>` is the version prefix of the out-of-order file (e.g., `20260227000000`)
- **AND** the script SHALL re-scan for remaining out-of-order files after each rebase invocation (since rebase renames files and rewrites `atlas.sum`)
- **AND** the script SHALL update `kustomization.yaml` to reference the new filenames
- **AND** `atlas.sum` SHALL be recalculated by the rebase command

#### Scenario: Auto-fix with no issues found

- **WHEN** `--fix` is passed but no out-of-order files are detected
- **THEN** the script SHALL take no action and exit with zero status

### Requirement: The system MUST integrate with Claude Code hooks

A Claude Code hook SHALL invoke the migration drift check with `--fix` after successful `git rebase origin` operations in the backend repository. The hook SHALL NOT fire on `git rebase --abort`, `git rebase --continue`, or interactive rebases.

#### Scenario: Developer rebases branch onto main via Claude Code

- **WHEN** a `git rebase origin/main` command completes successfully in the backend repo
- **THEN** the hook SHALL run `scripts/check-migration-drift.sh --fix`
- **AND** any out-of-order migrations SHALL be automatically rebased

#### Scenario: Rebase fails with merge conflicts

- **WHEN** a `git rebase origin/main` command fails due to merge conflicts
- **THEN** the script SHALL detect the incomplete rebase state (`.git/rebase-merge` or `.git/rebase-apply`)
- **AND** the script SHALL exit early without modifying migration files
