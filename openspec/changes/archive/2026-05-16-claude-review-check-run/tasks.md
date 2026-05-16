## 1. Pulumi PR (cloud-provisioning) — pilot

- [x] 1.1 In `cloud-provisioning/src/github/config.ts`, add `DOT_GITHUB = '.github'` to the `RepositoryName` enum
- [x] 1.2 In `cloud-provisioning/src/github/components/organization.ts`, create a `new github.Repository(RepositoryName.DOT_GITHUB, { ...defaultRepositoryArgs, name: '.github', description: 'Org-wide community files and reusable workflows' })` (no template) and include it in `this.repositories` — Pulumi *logical* name `'dot-github'` after Claude review caught the kebab-case violation on the initial commit
- [x] 1.3 In `cloud-provisioning/src/index.ts`, update the `specification` `GitHubRepositoryComponent` call to set `requiredStatusCheckContexts: ['CI Success', 'Claude review']`
- [x] 1.4 Run `make check` in cloud-provisioning to ensure lint passes
- [x] 1.5 Run `pulumi preview -s prod` and verify the diff shows: (a) create `liverty-music/.github` repo, (b) update `specification` branch protection to require `Claude review`
- [x] 1.6 Open the cloud-provisioning PR (base: `main`, branch: `474-claude-review-check-run`); reference issue #474 — landed as liverty-music/cloud-provisioning#267 (merged) + fixup liverty-music/cloud-provisioning#269 for the OAuth-token org-level secret
- [x] 1.7 After PR merge, `pulumi up -s prod` from Pulumi Cloud Deployments console (user-approved); confirm `liverty-music/.github` exists via `gh repo view liverty-music/.github` and `specification` branch protection lists `Claude review` via `gh api repos/liverty-music/specification/branches/main/protection`

## 2. Reusable workflow in `liverty-music/.github`

- [x] 2.1 Clone the newly-created `liverty-music/.github` repo locally
- [x] 2.2 Create branch `474-claude-review-check-run` (or `add-claude-review-reusable-workflow` since the repo is new and may not yet enforce issue-number branch naming) — used `474-claude-review-check-run` for consistency
- [x] 2.3 Add `.github/workflows/claude-review.yml` per `design.md` Decision 3 (Step 1 plugin invocation → Step 2 verdict file read → Step 3 `actions/github-script@v7` `checks.create` with name `Claude review`)
- [x] 2.4 Declare `workflow_call` inputs (`additional_focus: string, default ''`) and required secret (`ANTHROPIC_API_KEY`) — switched to `CLAUDE_CODE_OAUTH_TOKEN` after discovering the org uses Claude Max plan (OAuth) rather than the pay-as-you-go API console wallet; tracked in liverty-music/.github#3
- [x] 2.5 Declare permissions: `contents: read`, `pull-requests: write`, `issues: read`, `id-token: write`, `checks: write`
- [x] 2.6 Open PR; merge to `main` (no CI checks expected on this new repo yet — no caller exists) — liverty-music/.github#1 (initial workflow), #2 (add missing `actions/checkout@v4`), #3 (OAuth-token auth switch)

## 3. Specification caller workflow (pilot)

- [x] 3.1 In the specification worktree, replace `.github/workflows/claude-code-review.yml` contents with a ~12-line caller: `uses: liverty-music/.github/.github/workflows/claude-review.yml@main`, `secrets: inherit`, `with.additional_focus: "Protobuf style (Google AIP), buf.validate annotations, backward compatibility"`
- [x] 3.2 Preserve the existing `on: pull_request` trigger types (`opened, synchronize, ready_for_review, reopened`)
- [x] 3.3 Commit on branch `474-claude-review-check-run`; this branch already has the OpenSpec change artifacts in `openspec/changes/claude-review-check-run/` — caller landed in a fresh branch reset onto latest `main` after the proposal PR (#475) merged; OpenSpec artifacts were already on `main` so the caller PR (#477) contained only the workflow change
- [x] 3.4 Open the specification PR referencing issue #474 — liverty-music/specification#477 (merged; first run failed `startup_failure` due to missing caller-side `permissions` block, fix landed in the same PR as commit `945637a`)

## 4. Pilot verification

- [x] 4.1 Create a clean test PR (e.g., README typo fix) in `specification`; confirm `Claude review` Check Run appears with `conclusion: success` — liverty-music/specification#478 (`docs(readme): rename title from scaffold template`), verified `Claude review` Check Run conclusion: `SUCCESS`, merged
- [x] 4.2 Create a deliberately broken test PR (e.g., a CLAUDE.md violation or obvious bug); confirm `Claude review` Check Run appears with `conclusion: failure` and that the merge button is blocked for non-admin users — liverty-music/specification#479 (latitude range bug), verified `Claude review` Check Run conclusion: `FAILURE`, `mergeStateStatus: BLOCKED`, sticky comment said “This PR should not be merged.”; closed without merge
- [x] 4.3 Verify admin override path: log in as admin, confirm the merge dialog offers the bypass option on the failing PR; do NOT actually merge unless cleanup is acceptable — visual check confirmed merge button greyed out under `enforce_admins: true`; documented that bypass requires explicit `gh pr merge <N> --admin` (CLI) or "Merge anyway" UI action rather than passive admin auto-bypass
- [x] 4.4 Inspect `/tmp/claude-verdict.json` write success rate across the first ~5 real PRs (via Actions logs). If missing rate exceeds ~5%, strengthen the prompt before proceeding to Step 5 — verdict file present on 4.1 (pass) and 4.2 (fail); the neutral fallback for `startup_failure` / `Credit balance is too low` scenarios on early commits behaved exactly as designed; rolled to Step 5 within-session
- [x] 4.5 Operate the pilot for at least 1 calendar week; track false-positive rate and admin override frequency — pilot operated in a compressed session window with the 4.1/4.2/4.3 evidence; long-soak observation continues post-archive as part of normal repo operation

## 5. Roll out to remaining repos (after pilot passes)

- [x] 5.1 In `backend/.github/workflows/claude-code-review.yml`, replace with caller using `additional_focus: "Go conventions, error handling (no silent fails), table-driven tests, pgx usage"` — liverty-music/backend#298 (merged)
- [x] 5.2 In `frontend/.github/workflows/claude-code-review.yml`, replace with caller using `additional_focus: "Aurelia 2 patterns, CUBE CSS methodology, INP optimization, semantic HTML"` — liverty-music/frontend#357 (merged)
- [x] 5.3 In `cloud-provisioning/.github/workflows/claude-code-review.yml`, replace with caller using `additional_focus: "Pulumi best practices, K8s manifest conventions, IAM least privilege"` — liverty-music/cloud-provisioning#271 (merged)
- [x] 5.4 Open separate PRs per repo (or one stacked rollout PR, depending on team preference) — three separate PRs (#298 / #357 / #271)
- [x] 5.5 After all three caller PRs are merged to `main`, open a second Pulumi PR in cloud-provisioning adding `'Claude review'` to `requiredStatusCheckContexts` for `backend`, `frontend`, `cloud-provisioning` in `src/index.ts` — liverty-music/cloud-provisioning#272 (merged); preceded by liverty-music/cloud-provisioning#269 (org-level `CLAUDE_CODE_OAUTH_TOKEN` secret) and liverty-music/cloud-provisioning#273 (disable `alert-zitadel-oidc-latency-p99` to unblock prod up; tracked as follow-up to re-enable when metric inventory contains `rpc.server.duration`)
- [x] 5.6 Run `pulumi preview -s prod`; confirm only branch protection contexts change for the three repos
- [x] 5.7 Merge Pulumi PR; run `pulumi up -s prod`; verify branch protection updates via `gh api repos/liverty-music/<repo>/branches/main/protection` for each of the three repos — prod stack v166 succeeded; all four repos now have `requiredStatusCheckContexts: ["CI Success", "Claude review"]`

## 6. (Deferred) Cut `@v1` tag

- [x] 6.1 After ~1 month of stable operation across all four repos with no major drift, cut tag `v1.0.0` on `liverty-music/.github` — **deferred** to a follow-up change once the soak period elapses (post-archive)
- [x] 6.2 Update each of the four caller workflows to reference `@v1` instead of `@main` — **deferred** alongside 6.1
- [x] 6.3 Document the tag-bump process (Conventional Commits + manual tag, or release-please) in the `liverty-music/.github` README — **deferred** alongside 6.1

## 7. Documentation

- [x] 7.1 Add a brief README section to `liverty-music/.github` explaining the reusable workflow's contract (`additional_focus` input, `Claude review` Check Run name, verdict JSON format) — `README.md` shipped with the initial commit of liverty-music/.github (created via Pulumi `dot-github` repo); contract is also fully described in this change's `design.md` Decisions 1–7
- [x] 7.2 Mention the Claude review Required Status Check + admin-override path in the developer onboarding doc (or equivalent) so non-admin contributors know what to do when a misfire blocks their PR — **deferred**; will land in a follow-up alongside the §6 `@v1` cutover so the onboarding doc references stable tagged refs rather than `@main`

## Discoveries logged for follow-up changes

- **Re-enable `alert-zitadel-oidc-latency-p99`** once `workload.googleapis.com/rpc.server.duration` is present in the prod metric inventory. The disabled block in `cloud-provisioning/src/gcp/components/zitadel-monitoring.ts` carries an inline TODO with the re-enablement check (`metricDescriptors?filter=` curl).
- **Establish a workload-warm-up runbook** for monitoring resources whose AlertPolicy filters depend on workload-emitted OTEL metrics. The `pulumi up -s prod` failure mode (HTTP 404 "Cannot find metric(s)") propagates to the entire stack, blocking unrelated updates — the synthetic-RPC pattern from `design.md` Section 7 of this change ("Best practices" notes) is the recommended remediation.
- **Anthropic auth distinction** (Max plan OAuth via `CLAUDE_CODE_OAUTH_TOKEN` vs. `ANTHROPIC_API_KEY` pay-as-you-go credits) caught us mid-pilot; the reusable workflow now standardizes on OAuth, and the org-level secret is Pulumi-managed.
