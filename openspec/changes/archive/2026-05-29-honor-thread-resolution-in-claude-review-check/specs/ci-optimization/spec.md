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
