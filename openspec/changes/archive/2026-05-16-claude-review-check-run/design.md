## Context

Today every liverty-music repo runs a `claude-code-review.yml` workflow that calls `anthropics/claude-code-action@v1` with the `code-review@claude-code-plugins` plugin and the `--comment` flag, producing a sticky PR comment. The four YAML files are nearly identical; any behavior change touches four PRs.

Direct review of `action.yml` and the plugin source confirmed two limitations:

- `anthropics/claude-code-action@v1` exposes **no native input** for submitting a formal PR review (`APPROVE` / `REQUEST_CHANGES`). The full input set (34 entries) covers triggers, allowed tools, model, secrets, and signing — nothing maps to the GitHub Review API.
- The `code-review` plugin's `allowed-tools` declaration is `Bash(gh pr comment:*)` + `mcp__github_inline_comment__create_inline_comment` only. It does not include `gh pr review`, so it cannot produce a verdict review even if instructed to.

Branch protection and repo provisioning for all liverty-music repos are managed in `cloud-provisioning/src/github/components/{organization.ts,repository.ts}` and `cloud-provisioning/src/index.ts` via `@pulumi/github`. `GitHubOrganizationComponent` creates repos under an `if (env === 'prod')` guard; `BranchProtection` inside `GitHubRepositoryComponent` is gated by `if (environment === 'prod')` as well. The existing `requiredStatusCheckContexts` on every repo is `['CI Success']` (added by archive `2026-03-27-enforce-required-ci-checks`). `ANTHROPIC_API_KEY` is already provisioned as an `ActionsOrganizationSecret` with `visibility: 'all'`, so it is automatically available to any new repo in the org.

## Goals / Non-Goals

**Goals:**

- Surface Claude's review verdict as a green/red signal that is visible in the PR list and the PR Checks panel without opening the PR.
- Make the failing verdict block merges where appropriate (Required Status Check).
- Eliminate four-way duplication of the workflow YAML.
- Preserve the existing multi-agent review quality of `code-review@claude-code-plugins` (do not rewrite the plugin's analysis logic).
- Stay aligned with the prevailing pattern used by GitHub Copilot Code Review, CodeRabbit, Qodo, and Sentry Seer.

**Non-Goals:**

- Replacing the official `anthropics/claude[bot]` GitHub App with a custom App so that AI reviews could count toward Required Approvals. The community consensus is that bot identities should not satisfy human-reviewer requirements; this proposal explicitly does **not** pursue that path.
- Tagging the reusable workflow as `@v1` on day one. Initial callers reference `@main`; a versioned release is deferred until the workflow has been stable across all four repos for ~1 month.
- Adding inline-comment generation beyond what `code-review --comment` already produces.
- Migrating other CI workflows (deploy, lint, atlas-ci) to a reusable workflow at the same time. The scope is the Claude review only.

## Decisions

### 1. Publish the verdict as a GitHub Check Run, not as a formal PR review

A formal `APPROVE` / `REQUEST_CHANGES` review was the user's initial mental model but is **not** the path the community has converged on.

- GitHub Copilot Code Review explicitly always leaves a `Comment` review, never `Approve` or `Request changes`, citing the desire to prevent bot reviews from bypassing required-reviewer protections.
- CodeRabbit, Qodo, and Sentry Seer all post comments and (optionally) Check Runs, but do not submit formal review verdicts.
- A bot-issued `REQUEST_CHANGES` review requires a dismiss-or-counter-review every time the author re-pushes, which generates ongoing operator friction; a Check Run is naturally overwritten by the next run.
- A bot author cannot approve its own PR; for repos that auto-create PRs (Renovate-style), the approve path would silently break.

Publishing a `Claude review` Check Run achieves the same green/red visibility, plugs into branch protection's Required Status Check mechanism, leaves the human approval flow untouched, and aligns with the rest of the ecosystem.

**Alternative considered**: Have Claude itself call `gh pr review --approve` / `--request-changes`. Rejected for the reasons above and because the existing plugin's `allowed-tools` does not include `gh pr review`, forcing us to either fork the plugin or replace it with a hand-rolled prompt that re-implements the multi-agent quality gate.

**Alternative considered**: Improve the sticky comment header with a ✅/⚠️ glyph and stop there. Rejected because that does not put the signal in the PR list view and cannot be used as a merge gate.

### 2. Host the reusable workflow in a new `liverty-music/.github` repo

A `workflow_call` reusable workflow needs a stable address. The conventional GitHub home for org-wide community files (and shared workflows) is a repo literally named `.github` under the org. It is publicly referenceable by callers in the same org with no special token handling, and future org-wide files (`CONTRIBUTING.md`, SECURITY policy, issue templates) can live in the same place.

**Alternative considered**: Hosting it inside `specification` repo. Rejected because it conflates the protobuf API contract scope with CI tooling and complicates the spec repo's release tag cadence.

**Alternative considered**: A dedicated `liverty-music/shared-workflows` repo. Acceptable but introduces an extra repo before there is a second reusable workflow to justify it. We can split later if the `.github` repo accumulates too many concerns.

### 3. Use the existing `code-review@claude-code-plugins` plugin and add a small wrapper

The plugin already orchestrates multiple specialist agents (haiku/sonnet/opus) with built-in false-positive gating. Re-implementing that in a custom prompt would regress review quality. Instead, the reusable workflow keeps the plugin invocation as `Step 1` and adds two further steps:

1. Claude writes `/tmp/claude-verdict.json` with `{ "verdict": "pass" }` or `{ "verdict": "fail", "count": N, "summary": "<one-line>" }` — a deterministic 1-line contract chosen over parsing the comment body (resilient to plugin output changes).
2. An `actions/github-script@v7` step reads the JSON and calls `checks.create` with `conclusion: success | failure | neutral`, `name: 'Claude review'`.

If the verdict file is missing (Claude failed to write it), the Check Run conclusion is `neutral` so that the lack of signal is distinguishable from a real pass or fail.

**Alternative considered**: Parse the sticky comment with a regex (`/No issues found/`). Rejected because the comment text is plugin-owned and may evolve, while we control the verdict JSON contract.

### 4. Verdict-to-conclusion mapping

| Claude verdict             | Check Run `conclusion` | UI signal | Blocks merge (if required) |
|---|---|---|---|
| `pass`                     | `success`              | ✅ green  | No                          |
| `fail`                     | `failure`              | ❌ red    | Yes                         |
| missing / unparseable JSON | `neutral`              | ⚪ neutral | No                          |

`neutral` for missing verdicts means workflow plumbing issues do not block merges; they are visible but require manual triage rather than emergency override.

### 5. Pilot in `specification` before rolling out

`specification` has lower commit velocity than `backend` / `frontend`, so a misfire affects fewer in-flight PRs. After 1–2 weeks of stable operation (verdict file missing rate, false-positive rate, dismissal-via-admin frequency), add `'Claude review'` to the other three repos' `requiredStatusCheckContexts` in a follow-up Pulumi PR.

The Pulumi change to add `Claude review` for the other three repos is in scope of this change's `tasks.md` (under a Step 5 follow-up section) but can be executed as a separate PR after pilot validation.

### 6. Bypass policy: admin override only

`Allow specified actors to bypass required pull request reviews` stays **off** — no service-account-shaped escape hatch. When Claude misfires, a repo admin uses the standard `Allow administrators to bypass configured protections` toggle (or the per-PR override) to merge. This keeps the policy boundary cleanly at "human admin override".

### 7. Anthropic API key

`ANTHROPIC_API_KEY` already exists as an `ActionsOrganizationSecret` (`visibility: 'all'`). The new `.github` repo automatically inherits it; no Pulumi change is required for secret distribution. The caller workflows pass `secrets: inherit` to forward it into the reusable workflow.

## Risks / Trade-offs

**[Risk] Claude does not write `/tmp/claude-verdict.json`** → the Check Run is `neutral`, which does not block merges. Reviewers may not notice that the verdict was never produced.

→ **Mitigation**: The Check Run title is `'No verdict produced'` for the neutral case. After ~5 PRs we will measure the missing rate; if it exceeds ~5%, strengthen the prompt (e.g., require the JSON to be emitted before declaring success) or add a stdout-log-based fallback parser.

**[Risk] Plugin output format drifts** → the `--comment` post may break, but the verdict JSON contract is ours.

→ **Mitigation**: The Check Run depends only on the JSON, not the comment text. Plugin drift affects the comment body but not the verdict signal.

**[Risk] Pilot-phase false positives block legitimate PRs** → `specification` is the smallest-blast-radius pilot target, and admin override is documented as the escape hatch.

→ **Mitigation**: Repo admin can bypass via the standard branch-protection admin toggle. We will track override frequency during pilot and tune the prompt if needed before rolling out.

**[Risk] `prod` stack deployment is required twice** → once to create `liverty-music/.github` and add `'Claude review'` to `specification`, and again (later) to extend `'Claude review'` to the other three repos.

→ **Mitigation**: Standard operating procedure. Both deployments are small, reviewable Pulumi PRs with explicit user-approved `pulumi up -s prod`.

**[Risk] Reusable workflow referenced as `@main`** → the four callers consume the tip of `main` in the `.github` repo, so a broken workflow change immediately affects all repos.

→ **Mitigation**: Acceptable during pilot (one caller). Before rolling out to all four repos, decide whether to switch to `@v1` tag pinning. Tracked in the change's open questions / Step 6.

## Migration Plan

1. Land the Pulumi PR (`cloud-provisioning`): creates `liverty-music/.github` repo and extends `specification`'s `requiredStatusCheckContexts` to `['CI Success', 'Claude review']`. Merge → dev auto-deploys (no GitHub-side effect because both changes are inside the `env === 'prod'` guards) → run `pulumi up -s prod` to apply.
2. Clone newly-created `liverty-music/.github`, land the reusable workflow PR.
3. Land the `specification` caller PR (replaces `claude-code-review.yml` with the `~12-line caller). At this point the pilot is live: the next PR to `specification` produces a `Claude review` Check Run, and a failing verdict blocks merge.
4. Operate for 1–2 weeks; collect verdict statistics (missing rate, failure rate, admin overrides).
5. If stable, land the second Pulumi PR adding `'Claude review'` to `backend` / `frontend` / `cloud-provisioning` `requiredStatusCheckContexts`; land the three caller PRs.
6. (Deferred) After ~1 month of stability on all four repos, tag `liverty-music/.github` `v1.0.0` and bump callers from `@main` to `@v1`.

**Rollback**: Either remove `'Claude review'` from `requiredStatusCheckContexts` (Pulumi PR + `pulumi up -s prod`) — the Check Run still publishes but no longer blocks merges — or revert the caller workflow to the previous direct invocation. The new `.github` repo and reusable workflow can remain unused indefinitely.

## Open Questions

- **When to cut `v1` tag?** Plan is "1 month stable across all four repos". Could be earlier if no drift is observed.
- **Should we capture verdict statistics centrally?** A future enhancement could append verdict JSON to a long-lived log (e.g., a status-summary issue or a small Google Sheet) for false-positive trend analysis. Out of scope for this change.
