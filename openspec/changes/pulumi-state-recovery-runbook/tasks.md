## 1. Pre-flight Verification

- [x] 1.1 Reviewed the §13.4 incident archive (`openspec/changes/archive/2026-05-11-self-hosted-zitadel/tasks.md` §13.4 + design.md) for the exact recovery sequence: pre-incident `stack export --version N`, merged-state JSON construction (combine current + missing + filter obsolete entries), `pulumi stack import`, scrub `__pulumi_raw_state_delta` from affected resources to avoid the provider panic, verify with clean `pulumi preview`. **Note**: the archive line records concrete counts (current 129, missing 85, 2 obsolete, 214 final) but the literal arithmetic doesn't add up; treat those numbers as an order-of-magnitude trace, not a canonical formula. The runbook itself documents the procedure in resource-count-agnostic terms.
- [x] 1.2 Confirmed Pulumi Cloud retains stack versions indefinitely (relied on by step 1 of the recovery procedure). The dev stack history shows 287+ versions retained at archive time.
- [x] 1.3 Confirmed the `previewPullRequests=true` setting is already enabled on `Pulumi.dev.deploy.yaml` (verified via `pulumi deployment settings pull -s dev` during the upstream `pulumi-deploy-safeguards` exploration that this change supersedes). This is the layer that already covers the "code-driven cascade in a PR" risk surface, removing the motivation for a deploy-time guard.

## 2. Runbook Authorship

- [ ] 2.1 Author `cloud-provisioning/docs/runbooks/pulumi-state-recovery.md` with the structure: (a) header + "STOP — try this first" prevention guidance steering operators to `pulumi destroy --target`, (b) `pulumi state delete --target-dependents` blast-radius footgun explanation with the §13.4 87-resource cascade as the worked example, (c) step-by-step recovery procedure (5 steps: snapshot, merge, import, scrub, verify) with copy-pasteable shell commands, (d) "what NOT to use this for" section explicitly saying the runbook is for state corruption recovery only, not for normal destroys.
- [ ] 2.2 Cross-link the runbook from `cloud-provisioning/CLAUDE.md` under the existing `## Operating Protocols` section, in a new sub-section like `### Pulumi State Recovery` that pointers at `docs/runbooks/pulumi-state-recovery.md`. The pointer text SHALL include the trigger (`pulumi state delete --target-dependents` consideration or post-incident recovery) so the agent matches it during planning.
- [ ] 2.3 Optionally cross-link from `cloud-provisioning/docs/runbooks/zitadel-break-glass.md` (the only other `pulumi state` adjacent runbook) so an operator already in the runbooks folder discovers it.

## 3. PR Hygiene

- [ ] 3.1 Open the `specification` PR with this OpenSpec change (proposal / design / specs / tasks); link the planned `cloud-provisioning` runbook PR in description.
- [ ] 3.2 Open the `cloud-provisioning` PR with the new runbook + CLAUDE.md cross-link; link back to the specification PR.
- [ ] 3.3 Run `openspec validate pulumi-state-recovery-runbook` and resolve any errors.
- [ ] 3.4 Run `openspec status --change pulumi-state-recovery-runbook`; confirm `isComplete: true`.

## 4. Archive

- [ ] 4.1 After both PRs merge, archive the OpenSpec change via `/opsx:archive` (only when `openspec status` reports `isComplete: true` per `feedback_openspec_archive_when_done.md`). The archive PR also folds `pulumi-state-recovery` capability into `openspec/specs/`.
