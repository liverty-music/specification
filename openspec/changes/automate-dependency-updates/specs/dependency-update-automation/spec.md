## Purpose

Defines how dependency updates are proposed, grouped, and merged across the liverty-music repositories without human intervention, and which dependencies are deliberately withheld from that automation because a green pipeline does not establish their safety.

## ADDED Requirements

### Requirement: Dependency updates are proposed automatically in every repository

Each of `backend`, `frontend`, `cloud-provisioning`, and `specification` SHALL have automated dependency update proposals enabled. Shared policy — scheduling, grouping of cross-cutting ecosystems, automerge defaults, and concurrency limits — SHALL be expressed once in an organization-level configuration and inherited by each repository, so that a policy change takes effect across all four without editing each repository. Repository-specific rules SHALL extend, and MAY override, the inherited policy.

The automation SHALL cover every dependency axis present in the repositories. As of this change those are: Go modules; Go `tool` directives; the Go toolchain; npm packages; npm `overrides`; GitHub Actions; Docker base images; mise tools; Pulumi providers; pre-commit hook revisions; Buf module dependencies recorded in `buf.lock`; and container image tags in kustomize manifests.

This enumeration is a statement of current coverage, not a closed set. Introducing a manifest that declares external dependencies in a form none of the above covers SHALL be treated as introducing a new axis requiring configuration, not as a dependency exempt from automation.

An axis whose declared versions are unresolvable floating references — for example a tool pinned to `latest` — cannot produce update proposals. Such declarations SHALL be replaced with concrete versions so the axis is actually covered rather than silently inert.

#### Scenario: A tool is declared as a floating reference

- **WHEN** a dependency is declared in a form that always resolves to the newest release, such as `latest`
- **THEN** no update proposal can be raised for it
- **AND** the declaration SHALL be considered non-conforming to this requirement until it is pinned to a concrete version

#### Scenario: A shared policy change is made

- **WHEN** the automerge policy or update schedule is changed in the organization-level configuration
- **THEN** the new policy SHALL take effect in all four repositories
- **AND** no per-repository configuration file SHALL require editing

#### Scenario: A dependency axis receives an upstream release

- **WHEN** a new version is published for a dependency in any of the nine covered axes
- **THEN** an update proposal SHALL be raised for it, unless that dependency is excluded by another requirement in this specification

#### Scenario: A repository needs a rule the others do not

- **WHEN** a repository requires a grouping or automerge rule specific to its own stack
- **THEN** that rule SHALL be expressible in the repository's own configuration
- **AND** the inherited organization-level policy SHALL continue to apply to everything the rule does not address

### Requirement: Version-coupled dependencies are proposed as a single unit

Dependencies that must move together to remain functional SHALL be proposed in a single pull request rather than individually. A set of dependencies is version-coupled when upgrading a strict subset of it leaves the repository in a state that does not build, does not pass its tests, or behaves inconsistently.

At minimum, the following SHALL each be treated as one unit: the OpenTelemetry Go modules (core and contrib together); the Connect-RPC Go modules; the Aurelia packages; the Vitest packages; the Storybook packages; the Vite plugin set; the stylelint configuration and plugin set; the workbox packages, including those split across `dependencies` and `devDependencies`; the OpenTelemetry JavaScript packages; and the Pulumi provider set.

#### Scenario: One member of a coupled set is released

- **WHEN** a new version is published for one package in a version-coupled set
- **THEN** the resulting pull request SHALL upgrade every member of that set that has a compatible release available
- **AND** SHALL NOT upgrade that package alone

#### Scenario: A coupled set spans dependency types

- **WHEN** members of a version-coupled set appear in both `dependencies` and `devDependencies`
- **THEN** they SHALL still be grouped into one pull request

### Requirement: A single logical version is updated in every location it appears

Where one logical version is recorded in more than one file, all of its locations SHALL be updated by the same pull request. Updating a strict subset is prohibited, because the resulting pipeline would verify a configuration that does not match what is being proposed.

The following fan-outs SHALL each be bound into one unit:

- **Go version** — the `go` language directive and the `toolchain` directive in `backend/go.mod`, the builder image tag in `backend/Dockerfile`, the `go` setting in `backend/.golangci.yml`, and every `go-version` input across `backend`'s workflows (eight locations at the time of writing).
- **Node version** — every `node-version` workflow input across `frontend` and `cloud-provisioning`, every Node base image tag in `frontend`'s Dockerfiles, `cloud-provisioning`'s declared `engines.node` range, and the `@types/node` major in both repositories' manifests (fourteen locations at the time of writing).
- **Playwright version** — the `@playwright/test` package version, the Playwright container image tag used by the component-test CI job, and the same image tag in the documented baseline-regeneration command, which must match the CI job's image for baselines to be reproducible.

Because the locations of a fan-out record the version at differing precision — some carry a full patch version, others only major or major-minor — the unit SHALL define how a proposed version projects onto each location. A location whose recorded precision does not change under a given bump SHALL be treated as already satisfying that bump, and its unchanged state SHALL NOT be interpreted as a partial update.

The `@playwright/test` version SHALL be recorded as an exact version rather than a range, so that it cannot drift away from the container image tag without an explicit pull request.

#### Scenario: The Go minor version is upgraded

- **WHEN** an update crossing a Go minor version is proposed
- **THEN** the pull request SHALL update every Go-version location to the proposed version at that location's recorded precision
- **AND** the CI run for that pull request SHALL build and lint using the proposed version, not the previous one

#### Scenario: A bump does not alter a coarser location

- **WHEN** a patch-level bump is proposed and a location records only major or major-minor precision
- **THEN** that location SHALL remain unchanged
- **AND** the pull request SHALL still be considered a complete update of the unit

#### Scenario: Only part of a fan-out could be updated

- **WHEN** a new version is available for one location of a fan-out but cannot be applied to another location whose recorded precision would change
- **THEN** no partial pull request SHALL be raised

#### Scenario: A Playwright upgrade invalidates visual baselines

- **WHEN** a Playwright upgrade changes rendered output such that committed visual baselines no longer match
- **THEN** the CI gate SHALL fail
- **AND** the pull request SHALL NOT be automerged
- **AND** the pull request SHALL require a human to regenerate the baselines before it can proceed

### Requirement: Updates automerge only when the CI gate covers their risk

An update SHALL be merged without human review when its repository's `CI Success` gate passes, provided the gate actually exercises the behavior the update could break. An update SHALL require human review when its risk is not observable to the pipeline.

Minor and patch updates SHALL automerge by default, including the Aurelia release-candidate to general-availability transition and the external `pocketsign` schema SDK. Major updates SHALL NOT automerge.

The following SHALL be withheld from automerge regardless of version increment, for the stated reasons:

- **Pulumi provider updates** that produce a non-empty infrastructure preview — a type check cannot reveal that a provider upgrade would replace a live resource.
- **`@playwright/test` updates** — visual baselines require regeneration, which automation cannot perform.
- **Changes to npm `overrides` entries** — these encode a human judgment about a transitive advisory, and their correct resolution is often removal rather than upgrade.

#### Scenario: A minor update passes CI

- **WHEN** a minor or patch update's pull request reaches a passing `CI Success` gate
- **AND** the update is not withheld by this requirement
- **THEN** it SHALL be merged without human review

#### Scenario: A major update passes CI

- **WHEN** a major update's pull request reaches a passing `CI Success` gate
- **THEN** it SHALL remain open for human review

#### Scenario: A Pulumi provider upgrade would alter live infrastructure

- **WHEN** a Pulumi provider update is proposed and the infrastructure preview reports any resource change
- **THEN** the pull request SHALL NOT be automerged

#### Scenario: A Pulumi provider upgrade is inert

- **WHEN** a Pulumi provider update is proposed and the infrastructure preview reports no resource changes
- **AND** the `CI Success` gate passes
- **THEN** the pull request MAY be automerged

### Requirement: The liverty-music schema SDK is excluded from automated updates

The generated SDKs for the liverty-music schema — the `buf.build/gen/go/liverty-music/schema/*` Go modules and the `@buf/liverty-music_schema.*` npm packages — SHALL NOT have update pull requests raised for them.

These SDKs are advanced as part of the OpenSpec change that alters the schema, together with the consuming code that the schema change requires. `backend` and `frontend` SHALL be pinned to the same schema build; automated, independently-scheduled updates would break that correspondence and would not carry the accompanying code migration.

The exclusion SHALL be visible rather than silent: these dependencies SHALL continue to be reported as available-but-disabled, so that a schema release whose consumers were never advanced is detectable.

#### Scenario: A new schema build is published

- **WHEN** a new build of the liverty-music schema is published to the registry
- **THEN** no update pull request SHALL be raised in `backend` or `frontend`

#### Scenario: A consumer is left behind

- **WHEN** a schema build has been published and a consuming repository is still pinned to an earlier build
- **THEN** the drift SHALL be reported on the dependency dashboard

#### Scenario: An external schema SDK is published

- **WHEN** a new build of a third-party schema SDK, such as `buf.build/gen/go/pocketsign/apis/*`, is published
- **THEN** an update pull request SHALL be raised, because its release cadence is not controlled by this project

### Requirement: Proposal volume is bounded and scheduled

Update proposals SHALL be batched onto a recurring schedule rather than raised as upstream releases occur, and the number of simultaneously open update pull requests SHALL be capped. Updates that address a published security advisory SHALL be exempt from the schedule and raised as soon as they are available.

#### Scenario: Several upstream releases occur mid-week

- **WHEN** multiple dependencies publish new versions between scheduled runs
- **THEN** their proposals SHALL be raised together at the next scheduled run

#### Scenario: A security advisory is published

- **WHEN** an update resolves a published security advisory
- **THEN** its proposal SHALL be raised without waiting for the next scheduled run

#### Scenario: The open pull request cap is reached

- **WHEN** the number of open update pull requests has reached the configured cap
- **THEN** no further update pull requests SHALL be opened until some are merged or closed
