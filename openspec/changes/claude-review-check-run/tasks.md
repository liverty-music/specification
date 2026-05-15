## 1. Pulumi PR (cloud-provisioning) — pilot

- [ ] 1.1 In `cloud-provisioning/src/github/config.ts`, add `DOT_GITHUB = '.github'` to the `RepositoryName` enum
- [ ] 1.2 In `cloud-provisioning/src/github/components/organization.ts`, create a `new github.Repository(RepositoryName.DOT_GITHUB, { ...defaultRepositoryArgs, name: '.github', description: 'Org-wide community files and reusable workflows' })` (no template) and include it in `this.repositories`
- [ ] 1.3 In `cloud-provisioning/src/index.ts`, update the `specification` `GitHubRepositoryComponent` call to set `requiredStatusCheckContexts: ['CI Success', 'Claude review']`
- [ ] 1.4 Run `make check` in cloud-provisioning to ensure lint passes
- [ ] 1.5 Run `pulumi preview -s prod` and verify the diff shows: (a) create `liverty-music/.github` repo, (b) update `specification` branch protection to require `Claude review`
- [ ] 1.6 Open the cloud-provisioning PR (base: `main`, branch: `474-claude-review-check-run`); reference issue #474
- [ ] 1.7 After PR merge, `pulumi up -s prod` from Pulumi Cloud Deployments console (user-approved); confirm `liverty-music/.github` exists via `gh repo view liverty-music/.github` and `specification` branch protection lists `Claude review` via `gh api repos/liverty-music/specification/branches/main/protection`

## 2. Reusable workflow in `liverty-music/.github`

- [ ] 2.1 Clone the newly-created `liverty-music/.github` repo locally
- [ ] 2.2 Create branch `474-claude-review-check-run` (or `add-claude-review-reusable-workflow` since the repo is new and may not yet enforce issue-number branch naming)
- [ ] 2.3 Add `.github/workflows/claude-review.yml` per `design.md` Decision 3 (Step 1 plugin invocation → Step 2 verdict file read → Step 3 `actions/github-script@v7` `checks.create` with name `Claude review`)
- [ ] 2.4 Declare `workflow_call` inputs (`additional_focus: string, default ''`) and required secret (`ANTHROPIC_API_KEY`)
- [ ] 2.5 Declare permissions: `contents: read`, `pull-requests: write`, `issues: read`, `id-token: write`, `checks: write`
- [ ] 2.6 Open PR; merge to `main` (no CI checks expected on this new repo yet — no caller exists)

## 3. Specification caller workflow (pilot)

- [ ] 3.1 In the specification worktree, replace `.github/workflows/claude-code-review.yml` contents with a ~12-line caller: `uses: liverty-music/.github/.github/workflows/claude-review.yml@main`, `secrets: inherit`, `with.additional_focus: "Protobuf style (Google AIP), buf.validate annotations, backward compatibility"`
- [ ] 3.2 Preserve the existing `on: pull_request` trigger types (`opened, synchronize, ready_for_review, reopened`)
- [ ] 3.3 Commit on branch `474-claude-review-check-run`; this branch already has the OpenSpec change artifacts in `openspec/changes/claude-review-check-run/`
- [ ] 3.4 Open the specification PR referencing issue #474

## 4. Pilot verification

- [ ] 4.1 Create a clean test PR (e.g., README typo fix) in `specification`; confirm `Claude review` Check Run appears with `conclusion: success`
- [ ] 4.2 Create a deliberately broken test PR (e.g., a CLAUDE.md violation or obvious bug); confirm `Claude review` Check Run appears with `conclusion: failure` and that the merge button is blocked for non-admin users
- [ ] 4.3 Verify admin override path: log in as admin, confirm the merge dialog offers the bypass option on the failing PR; do NOT actually merge unless cleanup is acceptable
- [ ] 4.4 Inspect `/tmp/claude-verdict.json` write success rate across the first ~5 real PRs (via Actions logs). If missing rate exceeds ~5%, strengthen the prompt before proceeding to Step 5
- [ ] 4.5 Operate the pilot for at least 1 calendar week; track false-positive rate and admin override frequency

## 5. Roll out to remaining repos (after pilot passes)

- [ ] 5.1 In `backend/.github/workflows/claude-code-review.yml`, replace with caller using `additional_focus: "Go conventions, error handling (no silent fails), table-driven tests, pgx usage"`
- [ ] 5.2 In `frontend/.github/workflows/claude-code-review.yml`, replace with caller using `additional_focus: "Aurelia 2 patterns, CUBE CSS methodology, INP optimization, semantic HTML"`
- [ ] 5.3 In `cloud-provisioning/.github/workflows/claude-code-review.yml`, replace with caller using `additional_focus: "Pulumi best practices, K8s manifest conventions, IAM least privilege"`
- [ ] 5.4 Open separate PRs per repo (or one stacked rollout PR, depending on team preference)
- [ ] 5.5 After all three caller PRs are merged to `main`, open a second Pulumi PR in cloud-provisioning adding `'Claude review'` to `requiredStatusCheckContexts` for `backend`, `frontend`, `cloud-provisioning` in `src/index.ts`
- [ ] 5.6 Run `pulumi preview -s prod`; confirm only branch protection contexts change for the three repos
- [ ] 5.7 Merge Pulumi PR; run `pulumi up -s prod`; verify branch protection updates via `gh api repos/liverty-music/<repo>/branches/main/protection` for each of the three repos

## 6. (Deferred) Cut `@v1` tag

- [ ] 6.1 After ~1 month of stable operation across all four repos with no major drift, cut tag `v1.0.0` on `liverty-music/.github`
- [ ] 6.2 Update each of the four caller workflows to reference `@v1` instead of `@main`
- [ ] 6.3 Document the tag-bump process (Conventional Commits + manual tag, or release-please) in the `liverty-music/.github` README

## 7. Documentation

- [ ] 7.1 Add a brief README section to `liverty-music/.github` explaining the reusable workflow's contract (`additional_focus` input, `Claude review` Check Run name, verdict JSON format)
- [ ] 7.2 Mention the Claude review Required Status Check + admin-override path in the developer onboarding doc (or equivalent) so non-admin contributors know what to do when a misfire blocks their PR
