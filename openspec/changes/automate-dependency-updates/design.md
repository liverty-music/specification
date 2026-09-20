## Context

See `proposal.md` — Why. The relevant existing state:

- Four repositories (`backend`, `frontend`, `cloud-provisioning`, `specification`) plus an org-owned `.github` repository, all created by Pulumi in `cloud-provisioning/src/github/components/organization.ts`.
- Every CI workflow already terminates in a `CI Success` job using `re-actors/alls-green` with an `allowed-skips` list, and branch protection already requires exactly `['CI Success']` (`ci-optimization` spec). No CI restructuring is needed to make a single check authoritative.
- `.github` already hosts a reusable workflow consumed by all four repositories (`claude-review.yml`), so cross-repository configuration sharing is an established pattern here.
- Repository merge settings are `allowMergeCommit: true`, `allowSquashMerge: false`, `allowRebaseMerge: false`, with `deleteBranchOnMerge: true`.
- `frontend/.npmrc` points the `@buf` scope at `https://buf.build/gen/npm/v1/`.

## Goals / Non-Goals

**Goals:**

- One place to change shared update policy, inherited by all four repositories.
- Make `CI Success` mean what the automerge policy assumes it means, before any automerge is enabled.
- Express each multi-file logical version as one unit, so that a proposed version and the version CI exercises are always the same.

**Non-Goals:**

- Changing the `CI Success` gate mechanism, the `allowed-skips` pattern, or branch protection semantics. They already work; this change adds jobs behind the gate and enables auto-merge in front of it.
- Updating transitive (`// indirect`) Go dependencies individually.
- Bumping any dependency as part of this change. The change delivers the machinery; the first wave of updates arrives as its own pull requests.
- An AI triage layer over update pull requests (see `proposal.md` — Impact).

## Decisions

### D1: Renovate over Dependabot

Dependabot cannot read `mise` configuration files or `kustomize` manifests, both of which are live dependency axes here (`cloud-provisioning/.mise.toml`, `specification/.mise/config.toml`, `backend/k8s/`). It also cannot express cross-file grouping, which D4 depends on entirely. Renovate covers eleven of the twelve axes, supports arbitrary grouping, and supports regex-based custom managers. The twelfth, `buf.lock`, is covered by neither tool — Renovate has no Buf Schema Registry manager or datasource — so it is not a point of comparison between them; it stays manual under either choice (D7).

*Alternatives considered:* Dependabot — rejected on the coverage and grouping gaps above. A bespoke scheduled workflow generating update PRs — rejected because it would reimplement changelog fetching, version comparison, and grouping for twelve ecosystems, and the existing `bump-prod-pin.yml` shows how much workflow code a single well-defined bump already costs.

The Mend-hosted GitHub App is used rather than self-hosting: it is free for private repositories, and self-hosting would add an execution environment to operate for no capability this change needs.

### D2: Organization preset in `.github`, extended per repository

Renovate auto-detects `renovate-config.json` in an organization's `.github` repository and makes every repository extend it. Shared policy — schedule, concurrency caps, GitHub Actions / Docker / mise rules, automerge defaults — lives there. Each repository carries a small `renovate.json` holding only what is specific to its stack.

*Alternative considered:* a dedicated `renovate-config` repository (also auto-detected). Rejected because `.github` already exists, is already Pulumi-managed, and already serves this exact role for `claude-review.yml`. A second configuration repository would split the same concern across two places.

### D3: Grouping by version-coupled family, upstream first

The `dependency-update-automation` spec requires that version-coupled sets move as a unit, and separately that maintained upstream configuration is reused rather than reimplemented. Most of these families are already grouped by Renovate's own presets, which `config:best-practices` pulls in via `config:recommended` (D14). Local rules are written only where no upstream group exists.

**Covered upstream — no local rule:**

| Family | Preset |
|---|---|
| Storybook | `group:storybookMonorepo` |
| Vitest | `group:vitestMonorepo` |
| OpenTelemetry JS | `group:opentelemetry-jsMonorepo` |
| stylelint | `group:stylelint` |
| Pulumi | `group:pulumi` |

**Local rules — no upstream coverage:**

| Group | Members | Automerge |
|---|---|---|
| `otel-go` | `go.opentelemetry.io/otel{,/metric,/sdk,/trace}`, both OTLP exporters, `contrib/.../otelgrpc`, `contrib/.../otelhttp` | yes |
| `connectrpc-go` | `connectrpc.com/{connect,authn,cors,grpchealth,otelconnect,validate}` | yes |
| `go-tools` | `tool` directive entries: buf, delve, mockery, gofumpt | yes |
| `aurelia` | `aurelia`, `@aurelia/{i18n,router,testing,vite-plugin,storybook}` | yes |

`group:opentelemetry-go` exists but matches `github.com/open-telemetry/**`; `backend` imports `go.opentelemetry.io/*`, so it does not apply and the local `otel-go` group is required. Core-versus-contrib version skew (`v1.44.x` core against `v0.6x` contrib) is why that group matches by family rather than by version. No upstream group covers `connectrpc.com` or Aurelia.

`workbox` is in Renovate's monorepo registry (`googlechrome/workbox`), so `group:monorepos` covers it; `vite` and `connectrpc-js` are left to upstream coverage pending verification during the observation phase (D10). A local rule is added only if the observed PRs show them ungrouped.

`opentelemetry-go` is in that registry too, but pointing at `open-telemetry/opentelemetry-go` — the contrib modules live in a separate repository, so the registry would split core from contrib, which is exactly the coupling `otel-go` exists to preserve. The local rule stays for that reason, and the observation phase confirms whether it still needs to cover core as well.

`@biomejs/biome` is pinned to the same exact version in `frontend` and `cloud-provisioning`. Renovate cannot group across repositories, so the two are placed on the same schedule; they will be proposed as two PRs that land close together. Accepting brief skew is cheaper than the alternatives (a shared config package, or a custom cross-repo bump workflow) for a formatter.

*Ordering caveat:* preset rules are evaluated before `packageRules`, and once a preset sets a `groupSlug` a later rule cannot override it. Local rules must therefore target families the presets do not claim, rather than attempting to re-group ones they do.

### D4: Custom managers for the three version fan-outs

Go (8 locations), Node (14 locations), and Playwright (3 locations) are each bound into one Renovate group using regex custom managers over the workflow YAML, `.golangci.yml`, Dockerfiles, and `AGENTS.md`, combined with the native `gomod` / `npm` / `dockerfile` managers.

The Go unit must include `go.mod`'s `go` language directive alongside `toolchain`. Renovate's `gomod` manager treats the two as separate dependencies and will propose the `go` directive on its own, which is precisely the partial update the binding exists to prevent.

This is the load-bearing decision of the change. Without it, a lone `go.mod` `toolchain` bump produces a PR whose CI installs Go 1.27 via `setup-go`, then silently builds with the proposed toolchain because `GOTOOLCHAIN` defaults to `auto` — a green result that verified a configuration nobody proposed.

*Alternative considered:* deriving every location from a single source (`setup-go` supports `go-version-file: go.mod`; Dockerfiles could take a build arg). This is the better end state and removes the need for custom managers on the Go axis. It is deliberately not bundled here: it changes how CI resolves its toolchain, which is exactly the mechanism this change needs to be able to trust while it is being established. Recorded as follow-up work in `tasks.md`.

### D5: `@playwright/test` pinned exactly

`"@playwright/test": "^1.49.1"` currently resolves to 1.58.1 while `ci.yaml` hard-pins `mcr.microsoft.com/playwright:v1.58.1-noble`. The caret lets the two drift apart with no PR at all. Pinning exactly makes every Playwright move an explicit, reviewable PR that updates the package and the container tag together.

The unit has a third member: `frontend/AGENTS.md` documents the baseline-regeneration command with the same image tag. That tag is the "baseline-generation image" the CI comment names, so if the documented command drifts from the CI job, a human following the documentation regenerates baselines against a different renderer than the one that validates them — silently poisoning the committed PNGs. It is bound into the same group.

Playwright is excluded from automerge because a version bump changes Chromium's rendering and therefore invalidates the committed `toMatchScreenshot` baselines, which Renovate cannot regenerate. Grouping makes the failure honest — CI goes red, so automerge correctly declines — but a human must regenerate baselines to advance the PR. The `storybook-component-testing` spec already defines baseline adoption as a human action; this preserves that.

### D6: Infrastructure credentials never reach a dependency pull request

The constraint that shapes this decision is what a preview must do to produce a plan: install the stack's dependencies and execute its program. `Pulumi.prod.yaml` opens with `environment: liverty-music/prod`, so ESC resolves the Cloudflare, Zitadel, GitHub and GCP credentials at stack load. Whatever those dependencies contain therefore executes with production infrastructure credentials, and the shared environment cannot be narrowed per job.

An earlier draft gated Pulumi automerge on an empty preview, reasoning that this made "CI green" truthful for a provider upgrade. It did — but it also meant every Renovate pull request in `cloud-provisioning` would run `npm ci` against a just-published package and execute it with those credentials, before any person had read it. Renovate pushes to branches inside the repository, so the fork protections do not apply. That turns the dependency pipeline into a path for third-party code to reach production credentials, which is the category of risk this whole change exists to reduce.

**The preview therefore must not run on automated dependency pull requests.** That conclusion is unchanged. What changed is where it has to be enforced.

#### The preview is not in GitHub Actions

That draft also assumed the preview did not exist yet and would be built as a `pulumi-preview` job. It does exist: Pulumi Cloud Deployments has `previewPullRequests: true` on both stacks, with GCP reached by OIDC rather than a stored token.

| | dev | prod |
|---|---|---|
| `previewPullRequests` | true | true |
| `deployCommits` | true | *(absent — no apply on merge)* |
| trigger `paths` | `src/**`, `Pulumi.dev.yaml` | `src/**` |
| `skipInstallDependencies` | false | false |

Nothing in the repository records this. The settings exist only in the Pulumi Cloud console, and `docs/runbooks/pulumi-state-recovery.md` already cites a `Pulumi.dev.deploy.yaml` that was never committed — the runbook points at a file that does not exist.

Building the GitHub Actions job anyway was considered and rejected on three grounds: it previews twice per pull request; it would add a `PULUMI_ACCESS_TOKEN` secret where OIDC already works, trading a short-lived exchange for a stored long-lived credential; and, decisively, **it would not implement the control it was written to implement**. A GitHub Actions `if:` condition governs a GitHub Actions job. It has no effect on whether Pulumi Cloud runs a preview.

#### The control is a trigger path, and today it is accidental

Given `previewPullRequests: true` and `skipInstallDependencies: false`, a Renovate pull request *should* already be executing an unreviewed package against production credentials. It is not — because the trigger `paths` list `src/**` and a stack YAML, and a Renovate pull request touches only `package.json` and `package-lock.json`.

So the property D6 exists to guarantee holds today, by coincidence. Nobody chose it, nothing records it, and the obvious improvement — "a dependency change alters what the program does, so it should trigger a preview" — opens the exposure the moment someone acts on it. A safeguard that survives only until a reasonable person edits a config file is not a safeguard.

This change therefore makes it explicit rather than incidental:

- The deployment settings are committed as `Pulumi.{dev,prod}.deploy.yaml`, so the `paths` list is reviewable, diffable, and subject to the same gate as any other change.
- `Pulumi.prod.yaml` is added to the prod stack's `paths`. Its absence is a real gap in the opposite direction: a pull request editing only prod stack configuration changes what would be deployed and is previewed by nothing.
- Dependency manifests are deliberately NOT added, with the reason recorded inline next to the list — so the next person to consider adding them reads why they must not.

The consequence for automerge is unchanged: infrastructure provider updates are not automerged. That is not a loss. Pulumi was already the clearest case in D-series reasoning where a reviewer holds something the gate cannot supply — the preview output itself. The reviewer runs it, exactly as the pull request template and runbooks already prescribe.

*Alternatives considered:* gating the preview behind a GitHub Environment with required reviewers for bot pull requests — rejected because approving that job means approving execution of code the approver has not read, the same ceremony-instead-of-verification failure identified elsewhere in this change. Relying on the release-age delay alone — rejected because it shortens the window without closing it, and would make that delay load-bearing for a threat it was not designed to stop. Turning `previewPullRequests` off for prod and previewing only from GitHub Actions — rejected as a larger, riskier migration than the gap warrants, and it would lose the OIDC credential path.

*Separately:* `cloud-provisioning` CI ran `make lint-ts` only, while `make check` is `lint-ts test`, so the repository's vitest suite never ran on a pull request. That gap is real, unrelated to the preview, and closed by adding a `test` job.

### D7: Schema SDK exclusion is visible, not silent

`buf.build/gen/go/liverty-music/schema/*` and `@buf/liverty-music_schema.*` are set to `enabled: false` rather than added to `ignoreDeps`. Both suppress PRs, but `enabled: false` keeps the dependency listed on the dependency dashboard as disabled-with-an-update-available. That turns the exclusion into a drift detector: a schema release whose consumers were never advanced becomes visible instead of invisible.

`buf.build/gen/go/pocketsign/apis/*` is *not* excluded — it is a third-party schema on someone else's release cadence, where falling behind is the risk rather than the safeguard.

No `hostRules` are needed. `buf.build/gen/npm/v1/` answers unauthenticated — verified directly — and `frontend/.npmrc` carries no token, so there is no credential to supply for the dashboard to populate.

**The exclusion is scoped to `liverty-music/*`, deliberately, and is not widened to "BSR packages".** Excluding everything from the Buf Schema Registry would be simpler to state and would be wrong: the reason for excluding our own schema is that `backend` and `frontend` must sit on the same build and an independently-scheduled bump would break that correspondence while leaving the code migration undone. That reason is a property of *ours*, not of the registry. It does not transfer to `buf.build/gen/go/pocketsign/apis/*`, where nobody here controls the cadence and falling behind is the risk rather than the safeguard — nor to the third-party modules in `specification/buf.lock` (`bufbuild/protovalidate`, `googleapis/googleapis`), which sit on the same side of that line and are unautomatable for an unrelated reason: Renovate has no Buf Schema Registry manager or datasource at all. Those are advanced by `buf dep update`, run by a person, and named in the runbook (task 11.3).

### D8: The Go toolchain comment is documentation, not a constraint

`backend/go.mod` carries a ten-line comment recording nine `GO-2026-*` advisories fixed in 1.27.0. `toolchain` states a *minimum*, and Renovate only raises versions, so no automerged bump can reintroduce those advisories — the comment's security rationale is not at risk.

What does decay is the comment's literal claim ("Pin the minimum toolchain to 1.27.0") once the directive reads something else. Rather than trying to make a bot rewrite prose, the comment is reworded once to read as a floor-and-history record — why the floor was set where it was — with a line noting that the directive is advanced automatically. Its factual content then stays true across bumps.

### D9: `overrides` are left to humans

All four `frontend` `overrides` entries were inspected:

- `bfj` — dead; its origin (snarkjs, via the ZKP feature) was removed with `remove-blockchain-ticket-system`, and it no longer appears in the lockfile. Removed in the working tree with zero lockfile change.
- `minimatch` — origin equally dead, but **not** inert: `filelist@1.0.4` declares `minimatch: ^5.0.1`, and the override forces that transitive resolution to 10.2.4, five majors above what `filelist` asks for. Removal changes resolution and needs a lockfile regeneration plus verification on Node 22, so it is a task, not a cleanup.
- `dompurify` (`^3.4.13`) and `fflate` (`0.4.9`) — live security pins, both driven by `posthog-js`, which caps `fflate` at `^0.4.8`. `0.4.9` is the last release of that line, so the exact pin is not a mistake; there is nothing to upgrade to. Their correct end state is *removal* once `posthog-js` widens its range.

Renovate can raise a version inside an override but cannot decide that an override should cease to exist. So `overrides` are excluded from automerge, and keeping `posthog-js` itself current is treated as the root-cause remedy for two of the four.

### D10: Scheduling

Weekly groups run Saturday early morning JST, so results are reviewed Monday and CI contention is low. Monthly groups (Go version, Node version, GitHub Actions, mise) run at the start of the month. Vulnerability-remediating updates ignore the schedule. `prConcurrentLimit` caps simultaneous open PRs; automerge keeps the queue draining.

Expected steady state is roughly 36 PRs/month against roughly 100 ungrouped, with about 30 merging unattended.

### D11: `.github` is managed by Renovate but never automerged

`defaultRepositoryArgs` in `organization.ts` applies to all five repositories, so `allowAutoMerge: true` would reach `.github` as well. But `.github` has no `GitHubRepositoryComponent`: no branch protection, no `requiredStatusCheckContexts`, and no CI workflow of its own. Automerge there would mean merging with no gate whatsoever — the opposite of the policy this change implements.

`.github` is therefore included in Renovate (it consumes GitHub Actions in `claude-review.yml`, which should stay current) with automerge explicitly disabled for that repository in the organization preset.

*Alternative considered:* building CI and branch protection for `.github` so it can participate normally. Rejected as scope: verifying a reusable workflow meaningfully requires deciding what "passing" means for a workflow that only runs in other repositories' contexts, which is its own design problem. Recorded as a follow-up.

### D12: Coarse version locations are left coarse

Go and Node versions are recorded at differing precision — `toolchain go1.27.0` and `go-version: "1.27.0"` carry a patch, while `golang:1.27-alpine`, `go: '1.27'`, `node:22-alpine` and `engines.node` carry only major or major-minor. A patch bump therefore changes some locations and not others.

These are left as they are rather than pinned to patch precision. A floating minor tag resolves to the newest patch at build time, so the Docker builder picks up patch fixes without a commit, and `.golangci.yml`'s `go:` setting is a language-version declaration where patch precision carries no meaning. The spec's projection rule makes this explicit: a location whose recorded precision does not change under a bump is already satisfied, and its unchanged state is not a partial update.

*Alternative considered:* pinning every location to patch precision for byte-reproducible builds. Rejected because it converts every Go and Node patch release into a Dockerfile commit, for a reproducibility guarantee the project does not currently claim anywhere else.

### D13: Renovate rebases its own pull requests in `cloud-provisioning`

`cloud-provisioning` alone sets `requireUpToDateBranch: true`, deliberately — the comment records that it prevents Pulumi from deleting resources added by a recently merged PR that a stale branch does not know about. That flag is load-bearing and stays.

Under a strict up-to-date check, an automerge candidate goes stale the moment anything else lands on `main`. Renovate is configured to rebase its pull requests when the base branch moves, so CI re-runs against current `main` and the merge proceeds. This costs extra CI runs; `cloud-provisioning`'s pipeline is lint, test and preview only, so the cost is acceptable.

The interaction with the prod `RepositoryRuleset` matters: its sole bypass actor is the org-owned ci-bot App, and Renovate is not that actor. Renovate's merges therefore go through the ruleset normally rather than around it — which is the intended behavior, and means an automerge is subject to exactly the same gate as a human merge.

*Alternative considered:* removing `requireUpToDateBranch`. Rejected outright — it exists to prevent a specific, documented class of infrastructure accident.

### D14: `config:best-practices` is the baseline, not a blank sheet

The configuration extends Renovate's maintained `config:best-practices` preset rather than being assembled from scratch. That preset supplies, without local maintenance:

| Included preset | What it gives us |
|---|---|
| `config:recommended` | the maintained monorepo and family groupings D3 now defers to |
| `security:minimumReleaseAgeNpm` | a publication-age delay before npm releases are proposed |
| `helpers:pinGitHubActionDigests` | SHA pinning for third-party Actions (D15) |
| `docker:pinDigests` | digest pinning for container images |
| `:pinDevDependencies` | exact versions for dev tooling |
| `:maintainLockFilesWeekly` | scheduled lock file refresh |
| `abandonments:recommended` | flags dependencies that have stopped receiving releases |
| `:configMigration` | rewrites our own config when options are deprecated |

`security:minimumReleaseAgeNpm` scopes the delay to the npm datasource. That is where the risk is highest but not where it ends: Go modules, container images and GitHub Actions are all automerged here and all reachable by a compromised maintainer account. The delay is therefore configured across those datasources too, which is a project-specific addition rather than a reimplementation of the preset.

The release-age delay is the part this change most needed and did not have. Broad automerge removes the interval during which a human would ordinarily notice a compromised release; without a delay, a malicious npm publish could be proposed and merged the same day. Published analyses of supply-chain incidents put most windows of opportunity under a week, so a delay of a few days intercepts the majority. The weekly schedule (D10) already introduces an incidental lag, but incidental is not a control — and the vulnerability-remediation path that bypasses the schedule would bypass that lag too. The delay is configured explicitly so it survives a schedule change.

`:pinDevDependencies` generalises what D5 concluded for `@playwright/test`: a floating dev-tool version can drift without a pull request. Applying it repository-wide is the same reasoning, applied consistently.

*Alternative considered:* `config:recommended` alone. Rejected because the security-relevant additions — release age, digest pinning, SHA pinning — are exactly the ones this change needs, and they are the parts hardest to justify reimplementing locally.

*Consequence:* several decisions recorded earlier in this document became redundant when the preset was adopted, and D3 was rewritten to remove the duplicated groups rather than keep both.

### D15: Third-party Actions are pinned to SHAs, in this change

`helpers:pinGitHubActionDigests` is the one part of D14 with a large visible diff: 105 third-party `uses:` references across 21 workflow files in five repositories, of which exactly one is SHA-pinned today (`imjasonh/setup-crane@31b88efe…# v0.4` — so the practice is already understood here, just not applied).

A mutable tag means the action's owner can change what executes in CI at any time. These workflows hold GCP Workload Identity credentials, the ci-bot App credential, and — after D6 — a Pulumi token. Tag references are the weakest link in that set.

The pinning is not hand-written: enabling the preset makes Renovate raise the pinning pull requests itself, one per repository. The work is reviewing and merging them, not editing 105 lines. They are also a useful first exercise of the pipeline before automerge is enabled.

The CI run on this change's own pull request makes the case unprompted — it warns that `actions/checkout@v4` and `dorny/paths-filter@v3` target a deprecated Node 20 runtime, which is a stale-Action problem surfacing at exactly the moment we are deciding whether to automate Action updates.

*Alternative considered:* deferring pinning to a follow-up. Rejected on the operator's instruction to include it, and because enabling the preset without accepting its pinning PRs would leave the configuration claiming a practice the repositories do not follow.

### D16: Aurelia stays on the release candidate

Earlier drafts of this change described automerging "the Aurelia release-candidate to general-availability transition". That transition does not exist to be automerged: `aurelia`'s `latest` dist-tag is `2.0.0-rc.2`, which is the version already in `package.json`. There is no GA release, and the only higher-numbered channel is `dev` (`2.1.0-dev.*`).

Upgrading to GA as part of this change was considered — it would have removed any prerelease-specific handling from the configuration — but it is not available to do.

No special configuration is added for this. Renovate's defaults already follow the channel a registry marks current, so the `latest` tag keeps the project on `2.0.0-rc.2` and off the `dev` train without a local rule. The observation phase verifies that; a rule is written only if the default proves otherwise. Adding one pre-emptively would be a hack guarding against behaviour that has not been observed.

When GA is published it arrives as an ordinary update within the existing range, and is governed by the same rule as anything else: automerge if the gate exercises what it could break. D17 records why that condition is not met today.

### D17: Aurelia automerge is gated on app-shell coverage

`frontend/test/app-shell.spec.ts` has two skipped tests covering that the landing page renders and that the layout has navigation and a viewport. Those are the assertions an Aurelia upgrade would most plausibly break, and they are the surface with the least other coverage.

Withholding Aurelia from automerge would repeat the mistake corrected elsewhere in this change — a reviewer reading an Aurelia version bump sees no more than the pipeline does. So the skipped tests are repaired as a required task and Aurelia automerge is gated on that, in the same shape as the workbox gate. What had been an open question is closed: once the governing rule existed, it applied here identically, and leaving it open was an inconsistency rather than a deferral.

### D18: Build-regenerated artefacts are not gated on freshness

Some generated files are committed to a repository even though the build regenerates them from scratch on every run. No CI check asserts that the committed copy matches what a regeneration would produce, and none is added, because such a check would make every dependency update pull request red.

The mechanism is direct: a dependency bump changes the tree the generator reads, so the artefact's correct content changes with it. Renovate proposes the manifest and lock file change but cannot regenerate the artefact, so a freshness gate fails on exactly the pull requests this change wants to automerge — and fails them for a reason that has nothing to do with whether the update is safe. Automerge stops working across the board, and the only ways out are to disable the gate again or to hand-run the generator on every update.

What such a gate would protect is already protected. `frontend/src/generated/oss-licenses.json` is the worked example: `package.json` wires `"prebuild": "npm run licenses:generate"`, and `frontend/Dockerfile` runs `npm run build`, so the shipped image regenerates the file from the tree `npm ci` actually installed. The stale committed copy never reaches production. It is committed for a different reason entirely — `src/routes/legal/licenses-route.ts` imports it statically, so the file must exist for the dev server and Vitest to resolve the module. Its committed *content* is not what anything depends on.

The project has already classified these files this way. `frontend/.github/workflows/claude-code-review.yml` carries `paths-ignore: ['**/oss-licenses.json']` under the comment "Skip review on generated / machine-managed files to cut review noise" — the same judgement, applied to review rather than to CI.

On-disk drift is therefore accepted rather than tracked. It exists today and is harmless: on `origin/main` the committed `oss-licenses.json` records `@bufbuild/protobuf` at `2.14.1` while the lock file beside it resolves `2.15.0`. It is resolved opportunistically, when someone's build happens to produce the diff, and is not actively chased.

*Alternatives considered:*

- **Have Renovate regenerate the artefact via `postUpgradeTasks`.** Not available to rely on. The commands are gated by `allowedCommands`, which is a self-hosted-only administrative option — "If this list is empty then no tasks will be executed." On the Mend-hosted app selected in D1, that list is Mend's, not ours: the documentation states only that "a limited set of approved `postUpgradeTasks` commands are allowed in the app. The commands are not documented, as they may change over time." **Requires verification** whether any command capable of regenerating a project artefact is on that allowlist; it can only be determined by reading the `allowedCommands` line in Renovate's own log output, which cannot be done before the app is installed (task 5.4). Until then this option is treated as unavailable, and even if a usable command were found, an undocumented allowlist that "may change over time" is not a foundation for the automerge policy.
- **Add the freshness gate and accept the red pull requests.** Rejected: it trades the entire automerge policy for a property the build already guarantees.
- **Stop committing the artefact.** This is the correct remedy *if* the drift ever becomes a practical nuisance — `gitignore` it, and generate it on the dev and test paths as well as the build, so the static import still resolves. Recorded here so that a future contributor who notices the drift reaches for this rather than for a freshness gate. It is not done now because nothing currently depends on the committed copy being accurate, so the change would be cost without benefit.


## Risks / Trade-offs

- **A custom manager's regex silently stops matching** after a workflow is reformatted, so one location of a fan-out is quietly left behind — the exact failure the grouping exists to prevent. → Add an assertion that fails CI when the Go-version locations disagree with `go.mod`, so drift is caught by the pipeline rather than by a regex that matched nothing.
- **Automerge lands a green-but-wrong change** in an area CI does not observe. The audit found four such areas; three are closed here (WebKit, Pulumi preview, `cloud-provisioning` tests). The fourth was the PWA coverage, and re-verification found it worse than the audit recorded: the `pwa` project matched **zero specs**, because all three specs in `e2e/pwa/` sat in its `testIgnore`. CI was starting an empty project and reporting it green, so `workbox` and `vite-plugin-pwa` had no coverage at all rather than partial coverage. → Withholding them from automerge was considered and rejected: a reviewer opening a `workbox` bump sees a version and a lock file and cannot evaluate Service Worker behavior, so that route produces ceremony, not verification. The gap is closed instead.

  The recorded exclusion reason for `pwa-offline-cache.spec.ts` ("not available in CI headless") was indeed stale — `context.setOffline()` works in headless Chromium — but that was not what blocked it. `vite.config.ts` sets vite-plugin-pwa's `devOptions.enabled: false` and the e2e web server is the dev server, so no service worker existed to test; the spec failed with a blank page. Un-ignoring it, which is what task 2.5 originally prescribed, would have produced a red spec rather than coverage. The specs now run from `playwright.pwa.config.mjs` against `vite preview` over a production build.

  The assertions were rewritten at the same time, and this mattered more than the environment fix. The spec asserted `expect(bodyText).toBeTruthy()` — satisfied even when no service worker was ever registered — so it could not have detected a workbox regression had it been running all along. It now asserts the worker reaches `activated` and controls the page, and that the precache holds the app shell and its route chunks. It deliberately does not assert offline *navigation*: Playwright's offline emulation fails the top-level navigation before the service worker is consulted, and precache contents are what an upgrade actually breaks.

  The gap therefore splits. **`workbox` precaching is now covered.** `pwa-install-prompt.spec.ts` still genuinely cannot run — `beforeinstallprompt` depends on browser install heuristics — so `vite-plugin-pwa`'s *manifest / install-prompt* behaviour remains an enumerated gap, narrower than "PWA" and distinct from caching.

- **The WebKit gate this change adds is itself unreliable.** Once `webkit-repro` was actually executed, it proved intermittently red: 8 passes / 2 failures over 10 local runs, against 3/3 for `chromium-control`. The failure is the defect the spec exists to catch — the page-help bottom sheet dismissing itself shortly after opening, on real WebKit only — so the `IntersectionObserver` "just-opened" guard does not hold reliably. → Not mitigated here, and deliberately not retried away: `retries: 2` will usually mask it, which is precisely the failure mode this change is trying to eliminate elsewhere. It is recorded in `frontend/docs/ci-coverage-gaps.md` as an open product defect. Until it is fixed, WebKit-sensitive automerge rests on a gate that flakes, and the honest reading is that the WebKit gap is *narrowed*, not closed.
- **Grouped PRs are harder to bisect.** A ten-package OpenTelemetry PR that breaks a test gives a coarser signal than ten separate PRs. → Accepted: the packages cannot be upgraded separately anyway, so the finer signal was never actually available.
- **The preview resolves write-capable provider credentials through ESC, and running it executes the stack's dependencies** (D6). → The exposure is removed rather than narrowed: automated dependency pull requests do not trigger a preview, so third-party code never executes with those credentials. Residual risk is a malicious commit pushed directly to a branch by someone who already has write access.

  The sharp edge is that this protection is **one config line deep, in a file this project did not previously control**. It holds because the Pulumi Cloud trigger `paths` do not list dependency manifests, while `previewPullRequests: true` and `skipInstallDependencies: false`. Committing the deployment settings and recording the reason inline is the mitigation; it does not make the setting harder to change, only harder to change *unknowingly*. Anyone who adds `package.json` to that list re-opens the exposure, and no GitHub Actions configuration can prevent it — which is precisely why D6 rejected implementing the control there.
- **The org preset is the highest-leverage file in this change and sits in the least protected repository.** A careless or hostile edit to `renovate-config.json` silently changes automerge behaviour across four repositories. "Pulumi-managed" describes how `.github`'s settings are declared; it is not a review gate on commits landing in `.github`, which per D11 has no branch protection and no CI of its own. → Not mitigated by this change. Follow-up 12.4 (giving `.github` its own CI and protection) is the actual remedy, and this risk is the strongest argument for doing it.

## Migration Plan

1. **Land the CI hardening first** — WebKit projects, `cloud-provisioning` test and preview jobs, `@playwright/test` exact pin — and confirm `CI Success` still passes on an unrelated PR in each repository. Nothing about update automation is enabled yet, so this stage is reversible by reverting the workflow files.
2. **Install Renovate with automerge globally off.** Let the dependency dashboard populate and one full weekly cycle run. This reveals actual PR volume and catches custom-manager regexes that match nothing, without any merge risk.
3. **Enable `allowAutoMerge` in Pulumi and turn automerge on by group**, starting with `devDependencies` and GitHub Actions, then the coupled families, then the Go and Node version groups.
4. **Rollback**: at any stage, setting automerge off in the org preset stops unattended merges across all four repositories in one commit, leaving PR creation intact.

## Open Questions

- Whether the `specification` repository needs grouping rules at all beyond the inherited preset. Its dependency axes are GitHub Actions, mise, pre-commit hooks and `buf.lock`, all covered by the org preset; a repository-local `renovate.json` may turn out to be unnecessary.
- Whether `.github` should eventually get its own CI and branch protection so it can participate in automerge like the other four (D11).
