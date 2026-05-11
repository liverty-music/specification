## Why

During the `self-hosted-zitadel` cutover, an operator-side
`pulumi state delete --target-dependents` against ~9 expected Cloud-tenant
Zitadel resources cascade-removed 87 resources from Pulumi state — the
flag's blast radius was wider than expected (it follows ALL transitive
dependents, not just same-component-tree). Recovery required:

1. Snapshotting a pre-incident `pulumi stack export --version N`
2. Hand-merging the current state with the resources missing from it,
   filtering obsolete entries, to produce the recovery-target state
3. `pulumi stack import`-ing the merged JSON
4. Scrubbing `__pulumi_raw_state_delta` from the affected resources to
   work around a provider panic on import

Cumulative recovery cost: ~3 hours of operator time. The exact
procedure was reverse-engineered during the incident — it is NOT
documented anywhere, so the next operator hitting a similar incident
would have to rediscover it from cold.

This change ships the runbook so that the recovery procedure is captured
as institutional knowledge and the next state-recovery incident is a
~10-minute "follow the runbook" exercise instead of a multi-hour
forensic puzzle.

**This change does NOT add a deploy-time guard.** The original proposal
included a `preRunCommands` script that would count `delete + replace`
operations in `pulumi preview --json` and fail-close on threshold
breach. After review, we concluded the guard would not have prevented
the §13.4 incident (which happened via `pulumi state delete`, a
state-editing CLI command that bypasses both `preview` and `up`), and
the hypothetical "code-driven cascade in a PR" scenario the guard would
catch is already mitigated by:

- PR code review of the diff itself.
- Pulumi Cloud's `previewPullRequests=true` setting (already enabled),
  which posts the preview output (including delete counts) on every PR.
- Reviewer reading that preview output before merging.

Adding a fail-closed deploy-time guard would duplicate diligence that
already exists at the PR-review layer. The runbook addresses the
actual failure mode (operator-initiated `state delete` mishap) directly.

## What Changes

- **Add `cloud-provisioning/docs/runbooks/pulumi-state-recovery.md`** — operator
  runbook covering:
  - The `pulumi state delete --target-dependents` blast-radius footgun,
    with the §13.4 incident as a worked example.
  - Step-by-step recovery procedure: snapshot pre-incident version
    (`pulumi stack export --version N`), construct merged-state JSON,
    `pulumi stack import`, scrub `__pulumi_raw_state_delta` to avoid
    the provider panic, verify with a clean `pulumi preview`.
  - Preferred-path guidance: prefer `pulumi destroy --target` (which
    goes through the normal `preview → up` flow visible to PR reviewers
    via `previewPullRequests`) over `pulumi state delete` for
    intentional destroys. `pulumi state delete` is reserved for
    orphaned-resource cleanup (e.g. removing a resource the provider
    panic'd on), NOT for normal destroys.
  - Cross-link from `cloud-provisioning/CLAUDE.md` so future agents see
    the runbook under the existing operator-protocol section.

## Capabilities

### New Capabilities

- `pulumi-state-recovery`: Defines the operator runbook contract for
  Pulumi state corruption / cascade-delete recovery and the
  `pulumi state delete` vs `pulumi destroy --target` decision rule.

### Modified Capabilities

None.

### Removed Capabilities

None.

## Impact

**Affected resources**

- `cloud-provisioning/docs/runbooks/pulumi-state-recovery.md` (new) — operator
  runbook.
- `cloud-provisioning/CLAUDE.md` (modified) — add a one-line cross-link
  to the new runbook in the operator-protocol section.

**Affected workflows**

- Routine deploys: no change.
- An operator considering `pulumi state delete --target-dependents`:
  reads the runbook first, sees the blast-radius warning, prefers
  `pulumi destroy --target` instead.
- An operator who has already triggered a cascade incident: follows the
  runbook to recover instead of reverse-engineering the procedure.

**Reversibility**

- Pure documentation. Removable by a single `git revert`.

**Out of scope**

- A deploy-time guard against PR-merge cascades (originally proposed,
  dropped after review — PR review + Pulumi Cloud's
  `previewPullRequests` already cover this risk surface, and the §13.4
  incident path bypasses both `preview` and `up` so a deploy-time guard
  wouldn't have caught it anyway).
- General Pulumi policy-as-code (CrossGuard / Policy Packs) — different
  category of guardrail (per-resource invariants), separate change if
  ever needed.
- Stack-state backups — Pulumi Cloud already retains versions; the
  runbook leans on that, doesn't add to it.
- Automation around `pulumi state delete` discipline beyond runbook
  documentation.

**Dependencies**

- Independent. Lands in cloud-provisioning as a docs-only PR.
