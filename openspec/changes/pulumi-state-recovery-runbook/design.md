## Context

The `self-hosted-zitadel` cutover incident (`§13.4`, archived in
`2026-05-11-self-hosted-zitadel/tasks.md`) hit a `pulumi state delete
--target-dependents` blast-radius footgun: the flag follows ALL
transitive dependents (not just same-component-tree), so a delete
targeted at ~9 Cloud-tenant Zitadel resources cascade-removed 87
resources from Pulumi state — including GKE, Cloud SQL, GSM, IAM
bindings.

The recovery procedure was reverse-engineered live during the
incident:

1. Find a pre-incident `stack export --version N`.
2. Hand-merge it with the current state to produce the
   missing-resource superset, filtering obsolete entries (e.g. v1
   actions resources superseded after the cutover).
3. `pulumi stack import` the merged JSON.
4. Scrub `__pulumi_raw_state_delta` from affected resources to avoid
   a provider panic on the next operation.
5. Verify with a clean `pulumi preview` (empty diff = recovery
   succeeded).

(The §13.4 archive line records concrete counts — current 129, missing
85, 2 obsolete, 214 final — though the arithmetic doesn't quite add up
literally; treat those as an order-of-magnitude trace of the incident,
not as the canonical formula. The runbook itself documents the
procedure in resource-count-agnostic terms.)

This procedure is currently encoded only in the operator's head and a
few git commit messages. The next operator hitting the same incident
shape would have to rediscover it from the incident archive — a
multi-hour forensic exercise during what is likely already a
high-pressure scenario.

The fix this change ships is a single operator runbook
(`cloud-provisioning/docs/runbooks/pulumi-state-recovery.md`) capturing the
procedure end-to-end so the next incident is a "follow the runbook"
exercise.

## Goals / Non-Goals

**Goals:**

- Capture the §13.4 recovery procedure as a documented runbook so it
  can be followed without prior context.
- Document the `pulumi state delete --target-dependents` blast-radius
  footgun prominently so the next operator pauses before invoking it.
- Encode the operational discipline: prefer `pulumi destroy --target`
  (visible to PR reviewers via `previewPullRequests`) over
  `pulumi state delete` for any intentional destroy.

**Non-Goals:**

- A deploy-time guard. *(See D1 for the rationale; the original
  proposal included one and it was dropped after review.)*
- General Pulumi policy-as-code (CrossGuard) — different category of
  guardrail (per-resource invariants), separate change if ever
  needed.
- Stack-state backup automation — Pulumi Cloud already retains
  versions; the runbook leans on that.
- Improving Pulumi's own tooling (e.g. asking upstream to add a
  `--dry-run` to `state delete`). Out of scope; the runbook can
  recommend `--dry-run` adoption if/when upstream adds it.

## Decisions

### D1: No deploy-time guard — runbook only

**Choice:** Ship only the operator runbook. Do NOT add a
`preRunCommands` script or any Pulumi Cloud Deployments hook to fail
the auto-deploy when destructive ops exceed a threshold.

**Why (against the originally proposed guard):**

1. **The §13.4 incident bypassed the guard's protection path entirely.**
   `pulumi state delete --target-dependents` is a state-editing CLI
   command that runs on the operator's machine; it does not invoke
   `pulumi preview` or `pulumi up`, and Pulumi Cloud Deployments
   doesn't see it. A `preRunCommands` hook in the auto-deploy yaml
   would have done nothing during §13.4.
2. **For the hypothetical "code-driven cascade in a PR" scenario the
   guard *would* catch, four independent layers of diligence would
   already have to fail:**
   - PR author writes a destructive refactor.
   - Reviewer misses it in the code diff.
   - Pulumi Cloud's `previewPullRequests=true` posts the preview output
     (with delete counts) on the PR; reviewer misses it there too.
   - PR is merged.

   This compound failure is unlikely enough that adding a fail-closed
   automation primarily creates operational friction (override env
   var, threshold tuning, false-positive triage) without addressing a
   real-world gap.
3. **The actual incident motivates documentation, not gating.** The
   §13.4 incident was a tooling-misuse incident. The mitigation for
   tooling-misuse is "operator knows the tool's footguns" — runbook
   territory.

**What this means in practice:**

- The runbook prominently flags `pulumi state delete --target-dependents`
  as dangerous and steers operators to `pulumi destroy --target`
  instead.
- If a future incident shows that the PR-review + `previewPullRequests`
  layer is in fact insufficient, we can revisit the guard then with
  empirical motivation, not speculation.

### D2: Runbook lives in `cloud-provisioning/docs/runbooks/`

**Choice:** `cloud-provisioning/docs/runbooks/pulumi-state-recovery.md`
— co-located with the rest of the cloud-provisioning operator runbooks
(`zitadel-hang.md`, `zitadel-break-glass.md`,
`zitadel-oauth-client-recreate.md`, `add-zitadel-admin-user.md`).

**Why:**

- Pulumi Cloud is the deployment surface for cloud-provisioning. The
  runbook is operational documentation for that subsystem.
- Co-location with the existing zitadel runbooks at
  `cloud-provisioning/docs/runbooks/` keeps the operator's mental
  model simple: one folder for "things to read at 3 AM."
- Cross-references from `cloud-provisioning/CLAUDE.md` work without
  needing a URL.

**Alternative considered:** A repo-level `RECOVERY.md` at the root.
Rejected — operators looking for "how do I recover" will scan the
runbooks folder first; a root-level file is for project introduction,
not incident response.

## Risks / Trade-offs

- **[Risk]** A documentation-only change has no enforcement.
  Operators may still misuse `pulumi state delete --target-dependents`
  if they don't read the runbook. → **Mitigation**: cross-link from
  `CLAUDE.md` so the AI agent operating the repo sees the runbook
  during planning, before invoking destructive CLI commands. The
  same agent reads `CLAUDE.md` at session start.

- **[Risk]** The runbook captures the §13.4 procedure as it stood at
  recovery time. Future Pulumi versions may invalidate the
  `__pulumi_raw_state_delta` scrub step (e.g. if upstream fixes the
  provider panic). → **Mitigation**: the runbook calls out this step
  as a known-bug workaround with a date. Operator hitting it in a
  future Pulumi version checks whether the bug is still present
  before applying the workaround.

- **[Risk]** Operators in a hurry skip reading the warning section
  and jump straight to "the merge JSON command". → **Mitigation**:
  the runbook's first section is the prevention guidance (use
  `destroy --target`); the recovery procedure is gated behind a
  "STOP — try this first" section.

## Migration Plan

1. Author and PR `cloud-provisioning/docs/runbooks/pulumi-state-recovery.md`
   with the procedure transcribed from §13.4.
2. Add a one-line cross-reference from `cloud-provisioning/CLAUDE.md`
   to the new runbook in the operator-protocol section.
3. After merge, `/opsx:archive` this change.

**Rollback:** Pure documentation. Removable by `git revert`.

## Open Questions

1. **Does the §13.4 procedure generalize to other state corruption
   shapes?** The runbook captures `--target-dependents` cascade
   recovery; corruption from other sources (manual JSON edit, partial
   import failure) might need slightly different procedures. Initial
   scope: document the cascade case, note other shapes as a future
   addition.
2. **Should the runbook recommend always running `pulumi state delete
   --dry-run` first?** Pulumi has no `--dry-run` flag for `state
   delete` as of current versions. The runbook can recommend manual
   dependency inspection (`pulumi stack export | jq '...'`) as a
   stand-in.
