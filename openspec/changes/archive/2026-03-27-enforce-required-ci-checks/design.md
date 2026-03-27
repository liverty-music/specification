## Context

GitHub branch protection for all liverty-music repositories is managed via Pulumi in `cloud-provisioning/src/index.ts`, using the `GitHubRepositoryComponent`. Branch protection is only applied in the `prod` Pulumi stack (`if (environment === 'prod')`).

Current state of `requiredStatusCheckContexts`:

| Repository | Current Value | CI Success Job Exists? |
|---|---|---|
| backend | `['CI Success']` | Yes |
| frontend | `[]` | Yes |
| specification | `['CI Success']` | Yes |
| cloud-provisioning | `[]` | Yes |

All four repos have a `CI Success` aggregation job (using `re-actors/alls-green`) that gates on all other CI jobs. Cloud-provisioning additionally has Pulumi-managed preview checks reported by the Pulumi GitHub App:
- `liverty-music/dev - Update (preview)`
- `liverty-music/prod - Update (preview)`

## Goals / Non-Goals

**Goals:**
- Prevent merging PRs when CI checks fail, for frontend and cloud-provisioning repos.
- Achieve consistency: all four repos require `CI Success` to merge.

**Non-Goals:**
- Changing CI workflows themselves (no new jobs, no workflow modifications).
- Adding review approval requirements.
- Changing `requireUpToDateBranch` settings (cloud-provisioning already has `true`).

## Decisions

### 1. Use `CI Success` as the single required GitHub Actions check (all repos)

Every repo already has an `alls-green` aggregation job named `CI Success` that depends on all other CI jobs. Requiring only this one check is sufficient — if any upstream job (lint, test, e2e, etc.) fails, `CI Success` fails.

**Alternative considered**: Listing individual jobs (e.g., `Lint`, `Test`, `E2E`). Rejected because it creates a maintenance burden — every time a CI job is added or renamed, branch protection must be updated.

### 2. Do NOT add Pulumi preview as a required status check

**Investigation result**: Pulumi preview checks (`liverty-music/{stack} - Update (preview)`) are only posted by the Pulumi GitHub App when `src/**` files change. For k8s-only PRs (PR #176 confirmed), these checks do not appear at all. GitHub treats a missing required check as permanently "pending", which would block merge indefinitely.

**Decision**: Only require `CI Success` for cloud-provisioning. Pulumi preview checks remain informational — developers should verify them manually when Pulumi code changes.

**Alternative considered**: Creating a CI workflow that conditionally reports a `Pulumi Preview` success when no `src/**` changes are detected. This adds complexity and is out of scope for this change. Can be revisited later if needed.

## Risks / Trade-offs

**[Risk] Pulumi preview failures are not enforced** → A developer could merge a PR with a failing Pulumi preview.

→ **Mitigation**: Acceptable for now. Pulumi preview failures are visible on the PR. The `CI Success` check (which gates lint/typecheck) is the primary guard. Pulumi preview enforcement can be added later via a conditional CI job if needed.

**[Risk] Prod stack deployment required** → Branch protection only applies from the prod Pulumi stack. Running `pulumi up -s prod` is required.

→ **Mitigation**: Standard operational procedure. Preview first, then apply.
