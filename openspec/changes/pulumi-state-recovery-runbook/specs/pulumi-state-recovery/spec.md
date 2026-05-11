## ADDED Requirements

### Requirement: State-Recovery Operator Runbook

The `cloud-provisioning` repo SHALL maintain an operator runbook at `docs/runbooks/pulumi-state-recovery.md` documenting the procedure to recover from a corrupted-state Pulumi incident (e.g. an accidental `pulumi state delete --target-dependents` cascade), including:

- The blast-radius footgun pattern: `pulumi state delete --target-dependents` follows ALL transitive dependents, not just same-component-tree resources. The §13.4 incident (87 cascade-removals from ~9 intended) is documented inline as the worked example.
- Step-by-step recovery: (1) snapshot a pre-incident `pulumi stack export --version N`, (2) construct merged-state JSON by combining current state with the missing-resource superset (filtering obsolete entries as needed), (3) `pulumi stack import` the merged JSON, (4) scrub `__pulumi_raw_state_delta` from affected resources to avoid the provider panic, (5) verify with a clean `pulumi preview`.
- Preferred-path guidance: `pulumi destroy --target` SHALL be preferred over `pulumi state delete` for any intentional destroy. `destroy --target` goes through the normal `preview → up` flow, is visible to PR reviewers via Pulumi Cloud's `previewPullRequests=true`, and stays inside Pulumi's regular safety model. `pulumi state delete` is reserved for orphaned-resource cleanup (e.g. removing a resource the provider panic'd on), NOT for normal destroys.
- Cross-link from `cloud-provisioning/CLAUDE.md` so the AI agent operating the repo sees the runbook during planning, before invoking destructive CLI commands.

#### Scenario: Operator hits a state-cascade incident

- **WHEN** an operator misuses `pulumi state delete --target-dependents` and observes that more resources were removed than intended
- **THEN** the operator SHALL follow `docs/runbooks/pulumi-state-recovery.md` to restore the missing resources from a prior stack version
- **AND** following the runbook end-to-end SHALL restore the stack to the pre-incident state without further data loss

#### Scenario: Operator considers `pulumi state delete` for a planned change

- **WHEN** an operator reads the runbook for context on a planned state-edit change
- **THEN** the runbook SHALL direct them to `pulumi destroy --target` as the preferred path
- **AND** the runbook SHALL state explicitly that `state delete` is reserved for orphaned-resource cleanup, NOT for normal destroys

#### Scenario: AI agent reads CLAUDE.md before invoking destructive CLI

- **WHEN** an AI agent operating the `cloud-provisioning` repo reads `CLAUDE.md` at session start
- **THEN** the agent SHALL see a cross-link to `docs/runbooks/pulumi-state-recovery.md` in the operator-protocol section
- **AND** the agent SHALL be able to navigate to the runbook before considering any `pulumi state delete --target-dependents` invocation
