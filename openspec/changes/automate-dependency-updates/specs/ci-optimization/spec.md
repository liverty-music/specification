## ADDED Requirements

### Requirement: Every defined Playwright project is executed by CI

Every project defined in `frontend`'s Playwright configuration SHALL be executed by some CI job, or SHALL be removed from the configuration. A project that exists but is never invoked creates a coverage hole that is invisible in a passing run, because other projects may exclude specs on the stated grounds that the unexecuted project covers them.

In particular, the frontend CI SHALL exercise the WebKit engine. Specs excluded from a Chromium project because they are designated as engine-specific SHALL be executed by the WebKit project that is named as their owner, together with its Chromium control project.

The same obligation applies at spec granularity. A spec excluded from every project that would otherwise run it — whether by being omitted from all `testMatch` patterns or by appearing in a `testIgnore` list without a project that claims it — is uncovered, and SHALL be treated identically to an unexecuted project.

Where a project or an individual spec cannot run in CI — for example because it requires an authenticated storage state, or a browser capability such as Service Worker registration or an install prompt that is unavailable in headless CI — the configuration SHALL record that reason at the point of exclusion, and the resulting coverage gap SHALL be enumerated as a known gap rather than assumed covered. Automated merge policy SHALL treat a dependency whose behavior falls into an enumerated gap as unverified by the pipeline, regardless of the gate's result.

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
- **THEN** it SHALL be recorded as a known coverage gap with its reason
- **AND** dependencies governing the behavior it would have exercised SHALL NOT be treated as pipeline-verified

### Requirement: cloud-provisioning CI previews infrastructure changes

The `cloud-provisioning` CI workflow SHALL run an infrastructure preview on every pull request and SHALL report whether the change would alter any live resource. A type check alone SHALL NOT be treated as sufficient verification for a change to infrastructure code or to a provider dependency.

The preview SHALL run with read-only credentials and SHALL NOT apply changes. Its result SHALL be available as a distinct signal so that an automated merge decision can depend on whether the preview reported changes.

#### Scenario: A provider upgrade would replace a live resource

- **WHEN** a pull request upgrades a Pulumi provider in a way that would replace or destroy an existing resource
- **THEN** the preview SHALL report that resource change
- **AND** the pull request SHALL NOT be eligible for automated merge

#### Scenario: A change is infrastructure-inert

- **WHEN** a pull request's preview reports no resource changes
- **THEN** that result SHALL be distinguishable from a preview that reported changes

#### Scenario: Preview credentials are constrained

- **WHEN** the preview job runs
- **THEN** its credentials SHALL permit reading infrastructure state only
- **AND** SHALL NOT permit applying changes

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
