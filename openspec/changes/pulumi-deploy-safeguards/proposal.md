## Why

During the `self-hosted-zitadel` cutover, `pulumi state delete --target-dependents` was invoked against a small set of Cloud-tenant Zitadel resources (~9 expected). The flag's actual blast radius was 87 resources — it cascaded across every transitive dependent, including the GKE cluster, Cloud SQL `postgres-osaka`, GSM secrets, IAM bindings, and service accounts. Recovery required reconstructing a hand-merged stack JSON (current 129 resources + v246 missing 85 − 2 obsolete v1 actions = 214 resources) and `pulumi stack import`-ing it to v254, then scrubbing `__pulumi_raw_state_delta` from 177 resources after a provider panic on import (v255). Cumulative recovery cost: ~3 hours of operator time on what was supposed to be a routine cutover.

The Pulumi Cloud Deployments path that runs `pulumi up` on `main`-merge has no deploy-time guardrail against operations of this scale. Any future cutover or refactor that miscalculates `--target-dependents` blast radius can repeat this incident.

Two complementary safeguards close the gap:

1. **Operational runbook**: documented steps for state recovery (merged-state import, `__pulumi_raw_state_delta` scrub, version-replay verification) so the next operator does not have to reverse-engineer the procedure.
2. **Pre-deploy guard**: a Pulumi Cloud Deployments policy hook (or GitHub Actions check) that counts deletes/replaces in a `pulumi preview --json` and fails the deployment job when destructive operations exceed a configured threshold (proposed: 50). Threshold breaches require explicit human approval (re-run with an env-var override) before the deployment proceeds.

## What Changes

- **Add `cloud-provisioning/docs/pulumi-state-recovery.md`** — operator runbook covering:
  - The `pulumi state delete --target-dependents` blast-radius footgun (with the §13.4 incident as a worked example).
  - Step-by-step recovery: snapshot pre-incident version (`pulumi stack export --version N`), build merged-state JSON, `pulumi stack import`, scrub `__pulumi_raw_state_delta`, verify with a clean `pulumi preview`.
  - When NOT to use this: real intentional destroys (use `pulumi destroy` instead).
- **Add a pre-deploy delete-count guard** for Pulumi Cloud Deployments. Two implementation options, to be picked during `tasks.md` planning:
  - **(A)** Pulumi Cloud Deployments `pre-deploy` policy hook (per their policy-as-code feature) that runs `pulumi preview --json`, parses the operation counts, and fails the deployment if `deletes + replaces > THRESHOLD` unless the env var `PULUMI_DEPLOY_ALLOW_DESTRUCTIVE=1` is set on the deployment trigger.
  - **(B)** Pulumi Cloud's built-in deployment template `preRunCommands` running a small Bash/Node script that calls `pulumi preview --json | jq` to compute counts and exits non-zero on threshold breach. Less native than (A) but works without depending on Pulumi Cloud's policy-as-code feature being available on our subscription tier.
- **Threshold value SHALL be 50** as a starting point, sized to:
  - Comfortably accommodate routine multi-resource refactors (typical PR: 5–20 resources touched).
  - Trigger on rare but real cases (the `--target-dependents` cascade was 87 deletes; a future similar incident gets caught).
  - Tunable per stack (dev / staging / prod) if patterns differ.
- **Override mechanism** SHALL be an env var on the deployment trigger (`PULUMI_DEPLOY_ALLOW_DESTRUCTIVE=1`), NOT a stack config — config is harder to remove after one-time use and could become a permanent escape hatch.
- **`pulumi state delete` invocations** by operators SHALL be discouraged in the runbook in favor of `pulumi destroy --target` (which goes through the normal preview/apply flow and would be caught by the guard). The runbook shall document this preference and explain when `state delete` is still legitimate (orphaned resources from a hand-edited provider, never the normal path).

## Capabilities

### New Capabilities

- `pulumi-deploy-guardrails`: Defines the pre-deploy delete-count check, the threshold-tuning surface, and the operator runbook for state-recovery scenarios.

### Modified Capabilities

None.

### Removed Capabilities

None.

## Impact

**Affected resources**

- `cloud-provisioning/docs/pulumi-state-recovery.md` (new) — runbook.
- Pulumi Cloud Deployments configuration for `dev` and `prod` stacks — pre-deploy hook or preRunCommands wiring (depending on Option A vs. B).
- Pulumi Cloud Deployments configuration is currently checked into a repo file (per Pulumi Cloud's `pulumi-deployments-config.yaml` convention) or managed via the Pulumi Cloud console; this change shall pin it as code if it isn't already.

**Affected workflows**

- Routine PR merges (≤50 destructive ops): no behavior change.
- Rare-but-real bulk deletes / replaces: deployment fails with a clear message until a re-run with the override env var. Adds friction that is the entire point.
- Operators running `pulumi state delete` locally: no automatic guard (out of scope — local runs aren't Pulumi Cloud Deployments). Mitigation: runbook documentation.

**Reversibility**

- Each piece (runbook, guard) is additive and can be removed by a single revert.
- The guard's threshold is a config value, easy to tune up if it's too aggressive in practice.

**Out of scope**

- Pulumi Cloud Policy Packs that enforce specific resource patterns (e.g., "no public-IP buckets") — those are a different category of guardrail, separate change.
- Backups of stack state (Pulumi Cloud already retains versions; this change relies on that, doesn't add to it).
- Local-run safeguards (`pulumi destroy` from an operator's machine) — covered by the runbook documentation, not by automation.

**Dependencies**

- Independent of the other three follow-ups. MAY land first since it lowers the risk of the next bulk-rename / bulk-delete change (`rename-zitadel-machine-key-secret`, `k8s-naming-cleanup`).
