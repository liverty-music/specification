## MODIFIED Requirements

### Requirement: Claude review posts advisory inline comments on pull requests
The reusable workflow `liverty-music/.github/.github/workflows/claude-review.yml` SHALL invoke `anthropics/claude-code-action@v1` with the `code-review@claude-code-plugins` plugin and the `--comment` argument so that Claude posts inline review comments on each pull request. The workflow SHALL NOT create a GitHub Check Run, SHALL NOT emit a verdict file, and SHALL NOT submit a formal pull request review (`APPROVED` or `CHANGES_REQUESTED`).

The reusable workflow's `workflow_call` interface SHALL declare only the `CLAUDE_CODE_OAUTH_TOKEN` secret (no inputs). The workflow SHALL request permissions `contents: read`, `pull-requests: write`, `issues: read`, `id-token: write` — and SHALL NOT request `checks: write`.

The workflow SHALL match the shape of the official Anthropic example [`pr-review-comprehensive.yml`](https://github.com/anthropics/claude-code-action/blob/main/examples/pr-review-comprehensive.yml): a single job with a checkout step and a single `anthropics/claude-code-action@v1` step.

#### Scenario: PR is opened or updated
- **WHEN** a pull request is opened, synchronized, marked ready for review, or reopened
- **THEN** the caller workflow SHALL invoke the reusable workflow
- **AND** the reusable workflow SHALL run `anthropics/claude-code-action@v1` with the `code-review` plugin and `--comment`
- **AND** Claude SHALL post inline review comments (zero or more) on the PR's head commit
- **AND** no GitHub Check Run named `Claude review` (or any other name) SHALL be created by this workflow

#### Scenario: Claude finds no issues
- **WHEN** the Claude run completes and posts zero inline comments
- **THEN** the workflow run SHALL succeed
- **AND** Claude MAY post a top-level PR comment via `gh pr comment` per the `code-review` slash command's documented behavior

#### Scenario: Claude finds issues
- **WHEN** the Claude run completes and posts one or more inline comments
- **THEN** the workflow run SHALL succeed (the workflow does not fail on the presence of comments)
- **AND** reviewers SHALL treat the inline comments as advisory input alongside other reviewers' comments
- **AND** the PR's mergeability SHALL NOT be affected by the comments' presence or count

### Requirement: Branch protection gates merges on CI Success only
For every liverty-music repository whose `GitHubRepositoryComponent` participates in Claude review (`backend`, `frontend`, `specification`, `cloud-provisioning`), `cloud-provisioning/src/index.ts` SHALL set `requiredStatusCheckContexts` to `['CI Success']`. The string `'Claude review'` SHALL NOT appear in `requiredStatusCheckContexts` for any repo.

Branch protection is applied only when the Pulumi stack environment is `prod`; the Required Status Check is effective after `pulumi up -s prod`.

#### Scenario: PR has a failing CI Success check
- **WHEN** a pull request is open with `CI Success` Check Run `conclusion: failure`
- **THEN** the protected branch SHALL block merging
- **AND** the Claude review workflow's success or failure SHALL NOT affect mergeability

#### Scenario: PR has Claude inline comments but CI Success passes
- **WHEN** a pull request has Claude-posted inline comments (any count, any resolution state) AND `CI Success` Check Run `conclusion: success`
- **THEN** the protected branch SHALL allow merging
- **AND** no Claude-review-related Check Run SHALL be present in `gh api repos/.../branches/main/protection`'s required contexts

## REMOVED Requirements

### Requirement: Claude review publishes its verdict as a GitHub Check Run
**Reason**: Removed because `anthropics/claude-code-action` provides no upstream verdict / Check Run mechanism, and four iterations of user-side wrappers each introduced new bugs (LLM verdict confidence inflation, REST `commit_id` semantics not matching expected meaning, GraphQL `pull_request_review_thread` trigger silently disabling the workflow). The pattern is unsupported upstream; aligning with the upstream advisory-only pattern is the principled solution. See this change's `design.md` "Decision 1" for the full reasoning.

**Migration**: Reviewers read Claude's inline comments alongside other review input. There is no Check Run to consult, query, or override. Branch protection uses `CI Success` (deterministic) as the sole gate.

### Requirement: `Claude review` is enforced as a Required Status Check via Pulumi
**Reason**: Removed in conjunction with the Check Run itself. With no Check Run being created, leaving `'Claude review'` in `requiredStatusCheckContexts` would render every PR un-mergeable.

**Migration**: `cloud-provisioning/src/index.ts` updated to `requiredStatusCheckContexts: ['CI Success']` for all four repos. `pulumi up -s prod` applies the change before the reusable workflow is updated.

### Requirement: Claude review pilots on `specification` before all-repo rollout
**Reason**: Removed because the pilot-then-rollout posture only made sense when there was a gate to roll out. With no gate, there is nothing to pilot.

**Migration**: All four repos have the same advisory-only Claude review behavior from day one. No pilot phase.
