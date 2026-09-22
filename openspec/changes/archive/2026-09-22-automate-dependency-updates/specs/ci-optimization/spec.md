## ADDED Requirements

### Requirement: Every defined Playwright project is executed by CI

Every project defined in `frontend`'s Playwright configuration SHALL be executed by some CI job, or SHALL be removed from the configuration. A project that exists but is never invoked creates a coverage hole that is invisible in a passing run, because other projects may exclude specs on the stated grounds that the unexecuted project covers them.

In particular, the frontend CI SHALL exercise the WebKit engine. Specs excluded from a Chromium project because they are designated as engine-specific SHALL be executed by the WebKit project that is named as their owner, together with its Chromium control project.

The same obligation applies at spec granularity. A spec excluded from every project that would otherwise run it — whether by being omitted from all `testMatch` patterns or by appearing in a `testIgnore` list without a project that claims it — is uncovered, and SHALL be treated identically to an unexecuted project.

Where a project or an individual spec cannot run in CI — for example because it requires an authenticated storage state, or a browser capability genuinely unavailable in headless CI — the configuration SHALL record that reason at the point of exclusion, and the resulting coverage gap SHALL be enumerated as a known gap rather than assumed covered.

A recorded reason SHALL state a capability the CI environment actually lacks, and SHALL be re-verified rather than inherited. An exclusion justified by a claim that the tooling has since gained support for is a coverage gap with no cause, and the spec SHALL be returned to CI.

Each enumerated gap SHALL name the control that addresses it. Automated merge policy SHALL treat a dependency whose behavior falls into an enumerated gap as unverified by the pipeline, regardless of the gate's result; the named control, not the gate, is what permits such an update to proceed. Human review SHALL NOT be named as that control where the reviewer cannot observe the risk — for a version bump this leaves the gap uncovered while appearing to close it.

#### Scenario: A spec is excluded from one project as covered by another

- **WHEN** a Playwright project excludes a spec on the grounds that another project covers it
- **THEN** that other project SHALL be executed by a CI job

#### Scenario: A WebKit-only regression is introduced

- **WHEN** a change breaks rendering or interaction in WebKit but not in Chromium
- **THEN** the WebKit project SHALL fail
- **AND** the `CI Success` gate SHALL fail

#### Scenario: A project is defined but invoked nowhere

- **WHEN** the Playwright configuration defines a project that no CI job runs and whose configuration records no reason for being unrunnable
- **THEN** the configuration SHALL be considered non-conforming to this requirement

#### Scenario: A spec is excluded from every project that could run it

- **WHEN** a spec appears in a project's `testIgnore` and no other executed project matches it
- **THEN** it SHALL be recorded as a known coverage gap with its reason and its named control
- **AND** dependencies governing the behavior it would have exercised SHALL NOT be treated as pipeline-verified

#### Scenario: An exclusion reason no longer holds

- **WHEN** a spec is excluded on the grounds that CI lacks a capability, and the test tooling supports that capability in headless CI
- **THEN** the exclusion SHALL be removed and the spec returned to CI
- **AND** it SHALL NOT remain an enumerated gap

#### Scenario: A gap names human review as its control

- **WHEN** an enumerated gap names human review as the control addressing it, and the reviewable artefact is a version and lock file change
- **THEN** that control SHALL be considered insufficient
- **AND** the gap SHALL be addressed by restoring pipeline coverage

### Requirement: cloud-provisioning previews infrastructure changes on pull requests

Every pull request that a project member authors and that alters what the infrastructure stack would deploy SHALL be previewed, and the preview SHALL report whether the change would alter any live resource. A type check alone SHALL NOT be treated as sufficient verification for a change to infrastructure code.

This requirement does not prescribe where the preview runs. It MAY be produced by the repository's CI workflow or by the infrastructure tool's own pull-request integration. What it does require is that the set of inputs that trigger it actually covers what the stack reads: if stack configuration is an input to the deployed result, a pull request editing only stack configuration SHALL be previewed.

Running a preview requires installing the stack's dependencies and executing its program, so whatever code those dependencies contain runs with the credentials the preview resolves. Those credentials cannot be narrowed per job — the stack resolves its providers from a shared secrets environment — so the exposure is governed by controlling *which pull requests* reach the preview, not by scoping what the preview may do.

A pull request whose content was proposed by automation rather than written by a project member SHALL NOT be previewed. An automated dependency-update pull request introduces third-party code that has not been read by anyone, and previewing it would execute that code with production infrastructure credentials before any review. Pull requests originating from a fork SHALL likewise be excluded.

That exclusion SHALL be an explicit, recorded control, expressed in the same place the preview's trigger is configured and carrying its reason. An exclusion that holds only as an unstated side-effect of some other setting SHALL NOT be treated as satisfying this requirement: it is indistinguishable from an oversight, and the next person to revise that setting has nothing telling them what they would be removing.

The configuration carrying that control SHALL be version-controlled and subject to review, so that a change to it is visible as a change.

Consequently, infrastructure provider updates SHALL NOT be automatically merged. They SHALL be reviewed by a person, who obtains the preview by running it themselves — which is the workflow the repository's pull request template and runbooks already describe.

The preview job SHALL execute only the preview operation and SHALL contain no path that applies changes.

Its result SHALL be reported on the pull request so a reviewer can act on it.

#### Scenario: The exclusion holds only by coincidence

- **WHEN** automated pull requests are not previewed only because the trigger's input filter happens not to match the files such a pull request touches, and no record states that this is intended
- **THEN** the exclusion SHALL NOT be considered a control satisfying this requirement
- **AND** it SHALL be made explicit and recorded where the trigger is configured

#### Scenario: A pull request edits only stack configuration

- **WHEN** a project member's pull request changes only the stack's configuration, and that configuration is an input to what would be deployed
- **THEN** the preview SHALL run

#### Scenario: An automated dependency update touches the infrastructure stack

- **WHEN** an automated pull request proposes a new version of a dependency of the infrastructure stack
- **THEN** the preview job SHALL NOT run on that pull request
- **AND** the proposed dependency's code SHALL NOT execute with infrastructure credentials
- **AND** the pull request SHALL NOT be automatically merged

#### Scenario: A project member changes infrastructure code

- **WHEN** a project member opens a pull request changing the infrastructure stack
- **THEN** the preview SHALL run and report whether any live resource would change

#### Scenario: A change is infrastructure-inert

- **WHEN** a project member's pull request preview reports no resource changes
- **THEN** that result SHALL be distinguishable from a preview that reported changes

#### Scenario: The preview is inspected for an apply path

- **WHEN** the preview's configuration is inspected
- **THEN** it SHALL contain no path that applies infrastructure changes on a pull request or on merge

#### Scenario: A pull request originates from a fork

- **WHEN** a pull request is opened from a fork
- **THEN** the preview SHALL NOT run with infrastructure credentials available to the fork's code

### Requirement: cloud-provisioning CI runs its test suite

The `cloud-provisioning` CI workflow SHALL execute the repository's automated tests on every pull request. The workflow SHALL NOT invoke only a subset of the repository's declared verification steps while a broader step exists.

#### Scenario: A pull request breaks a unit test

- **WHEN** a pull request causes a `cloud-provisioning` test to fail
- **THEN** the `CI Success` gate SHALL fail

#### Scenario: The repository declares a fuller check than CI runs

- **WHEN** the repository declares a verification target that runs more than the CI workflow invokes
- **THEN** the CI workflow SHALL be considered non-conforming to this requirement

### Requirement: Automated merge is enabled through managed repository configuration

For every liverty-music repository participating in automated dependency merges, the repository's automatic-merge setting SHALL be enabled declaratively through the Pulumi-managed GitHub repository configuration in `cloud-provisioning`, rather than by changing the setting in the GitHub web interface.

Enabling automatic merge SHALL NOT weaken the existing merge gate: `requiredStatusCheckContexts` SHALL remain `['CI Success']`, and an automatically merged pull request SHALL satisfy exactly the same branch protection conditions as a manually merged one. The merge strategy used by an automatic merge SHALL be one the repository already permits.

#### Scenario: Automatic merge is requested on a pull request whose CI fails

- **WHEN** automatic merge is requested on a pull request and its `CI Success` check concludes as a failure
- **THEN** the pull request SHALL NOT be merged

#### Scenario: Automatic merge is requested on a pull request whose CI passes

- **WHEN** automatic merge is requested on a pull request and its `CI Success` check concludes successfully
- **THEN** the pull request SHALL be merged without further human action

#### Scenario: The automatic-merge setting is inspected

- **WHEN** a participating repository's settings are inspected
- **THEN** the automatic-merge setting SHALL be traceable to Pulumi source in `cloud-provisioning`
- **AND** re-running the Pulumi stack SHALL restore it if it was changed out of band
