## Purpose

Defines how dependency updates are proposed, grouped, and merged across the liverty-music repositories without human intervention, and which dependencies are deliberately withheld from that automation because a green pipeline does not establish their safety.

## ADDED Requirements

### Requirement: Dependency updates are proposed automatically in every repository

Each of `backend`, `frontend`, `cloud-provisioning`, and `specification` SHALL have automated dependency update proposals enabled. Shared policy — scheduling, grouping of cross-cutting ecosystems, automerge defaults, and concurrency limits — SHALL be expressed once in an organization-level configuration and inherited by each repository, so that a policy change takes effect across all four without editing each repository. Repository-specific rules SHALL extend, and MAY override, the inherited policy.

The automation SHALL cover every dependency axis present in the repositories for which the chosen tool provides a mechanism. As of this change those are: Go modules; Go `tool` directives; the Go toolchain; npm packages; npm `overrides`; GitHub Actions; Docker base images; mise tools; Pulumi providers; pre-commit hook revisions; and container image tags in kustomize manifests.

This enumeration is a statement of current coverage, not a closed set. Introducing a manifest that declares external dependencies in a form none of the above covers SHALL be treated as introducing a new axis requiring configuration, not as a dependency exempt from automation.

An axis the tool has no mechanism to read SHALL NOT simply be dropped from this list. It SHALL be recorded as a known gap, together with the named human control that covers it in the tool's place — otherwise an unautomatable axis is indistinguishable from one nobody thought of, and its absence reads as completeness.

Buf module dependencies recorded in `buf.lock` are such an axis at the time of writing: Renovate ships no manager or datasource for the Buf Schema Registry, and the entries are registry commit identifiers rather than versions, so no generic mechanism applies either. They are advanced by running `buf dep update` by hand, which the operational runbook names.

An axis whose declared versions are unresolvable floating references — for example a tool pinned to `latest` — cannot produce update proposals. Such declarations SHALL be replaced with concrete versions so the axis is actually covered rather than silently inert.

#### Scenario: An axis has no mechanism in the chosen tool

- **WHEN** a dependency axis exists in the repositories and the update tool provides no manager or datasource able to read it
- **THEN** the axis SHALL be recorded as a known gap rather than omitted from the enumeration
- **AND** the human action that advances it SHALL be named

#### Scenario: A tool is declared as a floating reference

- **WHEN** a dependency is declared in a form that always resolves to the newest release, such as `latest`
- **THEN** no update proposal can be raised for it
- **AND** the declaration SHALL be considered non-conforming to this requirement until it is pinned to a concrete version

#### Scenario: A shared policy change is made

- **WHEN** the automerge policy or update schedule is changed in the organization-level configuration
- **THEN** the new policy SHALL take effect in all four repositories
- **AND** no per-repository configuration file SHALL require editing

#### Scenario: A dependency axis receives an upstream release

- **WHEN** a new version is published for a dependency in any of the covered axes
- **THEN** an update proposal SHALL be raised for it, unless that dependency is excluded by another requirement in this specification

#### Scenario: A repository needs a rule the others do not

- **WHEN** a repository requires a grouping or automerge rule specific to its own stack
- **THEN** that rule SHALL be expressible in the repository's own configuration
- **AND** the inherited organization-level policy SHALL continue to apply to everything the rule does not address

### Requirement: Version-coupled dependencies are proposed as a single unit

Dependencies that must move together to remain functional SHALL be proposed in a single pull request rather than individually. A set of dependencies is version-coupled when upgrading a strict subset of it leaves the repository in a state that does not build, does not pass its tests, or behaves inconsistently.

Membership of this category SHALL be established by the declared constraints between the packages, not by how far apart their version numbers look. A family whose members depend on each other with a lower bound only — where the package manager resolves to the highest requested version and no upper bound exists — is NOT version-coupled, however uneven its numbering: upgrading one member alone still builds. A family whose members pin each other exactly, or bound each other from above, is.

At minimum, the following SHALL each be treated as one unit: the Aurelia packages; the Vitest packages; the Storybook packages; the Vite plugin set; the stylelint configuration and plugin set; the workbox packages, including those split across `dependencies` and `devDependencies`; the OpenTelemetry JavaScript packages; and the Pulumi provider set.

#### Scenario: A family's versions differ but its constraints do not bind

- **WHEN** members of a family carry visibly different version numbers, and each depends on the others with a lower bound only
- **THEN** the family SHALL NOT be treated as version-coupled
- **AND** a local grouping rule for it SHALL NOT override a maintained upstream grouping that separates them

#### Scenario: One member of a coupled set is released

- **WHEN** a new version is published for one package in a version-coupled set
- **THEN** the resulting pull request SHALL upgrade every member of that set that has a compatible release available
- **AND** SHALL NOT upgrade that package alone

#### Scenario: A coupled set spans dependency types

- **WHEN** members of a version-coupled set appear in both `dependencies` and `devDependencies`
- **THEN** they SHALL still be grouped into one pull request

### Requirement: A single logical version is updated in every location it appears

Where one logical version is recorded in more than one file, all of its locations SHALL be updated by the same pull request. Updating a strict subset is prohibited, because the resulting pipeline would verify a configuration that does not match what is being proposed.

**A duplicated version SHALL be eliminated rather than synchronised, wherever the toolchain can derive it from a single declaration.** Keeping copies in step needs a mechanism that keeps working — a pattern that must keep matching after a file is reformatted, and a check to catch it when it stops. Removing the copies needs nothing. Where a build or CI tool accepts a version file in place of a literal, that form SHALL be used, and the remaining declaration is the single source.

Only a version that genuinely cannot be derived SHALL be bound as a synchronised unit, and that binding SHALL be justified by the absence of a derivation, not chosen for convenience.

At the time of writing:

- **Go version** — `backend/go.mod` is the single source. `setup-go` reads it via `go-version-file`, and golangci-lint reads it when its `go` setting is absent. The builder image tag in `backend/Dockerfile` records the version at coarser precision and is managed as an ordinary container dependency, not as a copy to be synchronised.
- **Node version** — a version file per repository is the single source, read by `setup-node` via `node-version-file`. The Node base image tags and the declared `engines.node` range are ordinary dependencies at their own precision.
- **Playwright version** — NOT derivable, and therefore bound as a unit: the `@playwright/test` package version, the Playwright container image tag used by the component-test CI job, and the same image tag in the documented baseline-regeneration command. The third is prose in a contributor document, which no tool can derive, and it must match the CI job's image for committed visual baselines to be reproducible.

Because the locations of a fan-out record the version at differing precision — some carry a full patch version, others only major or major-minor — the unit SHALL define how a proposed version projects onto each location. A location whose recorded precision does not change under a given bump SHALL be treated as already satisfying that bump, and its unchanged state SHALL NOT be interpreted as a partial update.

The `@playwright/test` version SHALL be recorded as an exact version rather than a range, so that it cannot drift away from the container image tag without an explicit pull request.

#### Scenario: The Go minor version is upgraded

- **WHEN** an update crossing a Go minor version is proposed
- **THEN** the CI run for that pull request SHALL build and lint using the proposed version, not the previous one

#### Scenario: A duplicated version could be derived instead

- **WHEN** a version is repeated across files and the consuming tools accept a version file in place of the literal
- **THEN** the repetition SHALL be removed by deriving from a single declaration
- **AND** a pattern-matching rule to keep the copies in step SHALL NOT be introduced in its place

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

An update SHALL be merged without human review when its repository's `CI Success` gate passes, provided the gate actually exercises the behavior the update could break.

Where the gate does not exercise that behavior, the update SHALL be withheld from automerge only when a human reviewer can observe something the pipeline cannot. Human review is not a general-purpose substitute for missing coverage: for a dependency whose pull request contains only a version and a lock file, a reviewer sees strictly less than the pipeline does, and requiring their approval produces ceremony rather than verification. Where no reviewer can evaluate the risk, the correct response is to extend the pipeline's coverage, not to route the update through a person.

Minor and patch updates SHALL automerge by default, including the external `pocketsign` schema SDK. Major updates SHALL NOT automerge.

A dependency whose current version is a prerelease SHALL continue to track the release channel its registry marks as current, and SHALL NOT be advanced onto a less stable channel merely because that channel carries a higher version number. This is the tool's default behaviour and SHALL be verified rather than reimplemented.

The following SHALL be withheld from automerge regardless of version increment. Each qualifies because a reviewer holds information, judgement or agency the pipeline lacks:

- **Infrastructure provider updates** — the pipeline cannot preview them, because doing so would execute the proposed third-party code with production credentials (see the `ci-optimization` capability). A reviewer obtains the preview by running it themselves, which is information no gate can supply.
- **`@playwright/test` updates** — a reviewer can regenerate visual baselines and inspect the resulting diff, which automation cannot do.
- **Changes to npm `overrides` entries** — these encode a human judgement about a transitive advisory, and their correct resolution is often removal rather than upgrade.

#### Scenario: Coverage is missing and no reviewer could evaluate the risk

- **WHEN** an update's risk is not observable to the pipeline, and a reviewer inspecting the pull request would see only a version change and a lock file
- **THEN** routing the update through human review SHALL NOT be treated as a compensating control
- **AND** the gap SHALL be addressed by extending pipeline coverage

#### Scenario: A minor update passes CI

- **WHEN** a minor or patch update's pull request reaches a passing `CI Success` gate
- **AND** the update is not withheld by this requirement
- **THEN** it SHALL be merged without human review

#### Scenario: A major update passes CI

- **WHEN** a major update's pull request reaches a passing `CI Success` gate
- **THEN** it SHALL remain open for human review

#### Scenario: An infrastructure provider upgrade is proposed

- **WHEN** an update to an infrastructure provider dependency is proposed
- **THEN** it SHALL NOT be automerged regardless of the gate's result

#### Scenario: A prerelease dependency's channel advances

- **WHEN** a dependency tracked on a prerelease channel has a higher-numbered version available on a less stable channel
- **THEN** no update proposal onto that channel SHALL be raised

### Requirement: Releases are not adopted until they have aged

A newly published release SHALL NOT be proposed until a minimum period has elapsed since its publication. Automated merging removes the human pause during which a compromised release would ordinarily be noticed, so the delay is what replaces it: it gives registries, maintainers and scanners time to withdraw or flag a malicious publication before it reaches a repository.

The requirement applies with most force to npm, whose publication model allows a compromised maintainer account to ship arbitrary code to a large dependent base within minutes. It SHALL also apply to every other axis whose registry exposes a publication timestamp, including Go modules, container images and GitHub Actions — each of which is likewise reachable by a compromised maintainer account, and each of which this project automerges.

A release whose publication timestamp cannot be determined SHALL be treated as not having aged, rather than as having aged.

Exempting an update from the waiting period SHALL require a stated reason recorded in the configuration, and SHALL NOT be the default for any axis.

#### Scenario: A release is published and immediately proposed

- **WHEN** a dependency publishes a release less than the configured minimum age ago
- **THEN** no update proposal SHALL be raised for it yet

#### Scenario: A release has aged

- **WHEN** a release reaches the configured minimum age and its update is otherwise eligible
- **THEN** the update SHALL be proposed on the next scheduled run
- **AND** it SHALL be eligible for automerge under the normal policy

#### Scenario: A release carries no publication timestamp

- **WHEN** a release's publication time cannot be determined
- **THEN** it SHALL be treated as not yet aged

### Requirement: Maintained upstream configuration is reused rather than reimplemented

The automation configuration SHALL be built by extending the tool's maintained recommended configuration, adding only rules that express something specific to these repositories. A grouping, pinning or safety rule that the tool already maintains SHALL NOT be reimplemented locally.

The reason is drift: a locally copied group does not learn about packages added to the upstream family later, so it silently narrows over time while continuing to look correct. Local rules SHALL be reserved for package families the upstream configuration does not cover, for the version fan-outs described above, and for the automerge and exclusion policy, which are judgements about this project rather than facts about a package.

Where a local rule duplicates upstream coverage, the local rule SHALL be removed in favour of the upstream one.

#### Scenario: An upstream family gains a new package

- **WHEN** a package is added to a dependency family that the tool's maintained configuration groups
- **THEN** that package SHALL be grouped without any change to this project's configuration

#### Scenario: A local rule overlaps maintained configuration

- **WHEN** a local grouping rule covers a family the maintained configuration already groups
- **THEN** the local rule SHALL be considered non-conforming and removed

#### Scenario: A family has no upstream coverage

- **WHEN** a version-coupled family is not covered by any maintained group
- **THEN** a local rule for it SHALL be permitted

### Requirement: Third-party GitHub Actions are pinned to immutable references

Every third-party GitHub Action referenced by a workflow in any liverty-music repository SHALL be pinned to a full-length commit SHA rather than a mutable tag or branch. A tag can be repointed by its owner at any time, so a tag reference grants the action's owner the ability to change what executes in CI — including in the workflows that hold deployment and infrastructure credentials.

The pinned reference SHALL carry the human-readable version alongside it so the intended version remains legible, and SHALL be advanced by the same automation that proposes other updates.

Actions published from within the liverty-music organization are exempt, as their contents are already under this project's control.

#### Scenario: A workflow references an action by tag

- **WHEN** a workflow references a third-party action by a tag or branch
- **THEN** that reference SHALL be considered non-conforming to this requirement

#### Scenario: An upstream tag is repointed

- **WHEN** a third-party action's maintainer moves an existing tag to a different commit
- **THEN** the pinned workflows SHALL continue to execute the previously reviewed commit

#### Scenario: A pinned action publishes a new version

- **WHEN** a pinned third-party action publishes a release
- **THEN** an update proposal SHALL be raised that advances both the SHA and its accompanying version comment

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
