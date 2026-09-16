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

Dependabot cannot read `mise` configuration files or `kustomize` manifests, both of which are live dependency axes here (`cloud-provisioning/.mise.toml`, `specification/.mise/config.toml`, `backend/k8s/`). It also cannot express cross-file grouping, which D4 depends on entirely. Renovate covers all twelve axes, supports arbitrary grouping, and supports regex-based custom managers.

*Alternatives considered:* Dependabot — rejected on the coverage and grouping gaps above. A bespoke scheduled workflow generating update PRs — rejected because it would reimplement changelog fetching, version comparison, and grouping for twelve ecosystems, and the existing `bump-prod-pin.yml` shows how much workflow code a single well-defined bump already costs.

The Mend-hosted GitHub App is used rather than self-hosting: it is free for private repositories, and self-hosting would add an execution environment to operate for no capability this change needs.

### D2: Organization preset in `.github`, extended per repository

Renovate auto-detects `renovate-config.json` in an organization's `.github` repository and makes every repository extend it. Shared policy — schedule, concurrency caps, GitHub Actions / Docker / mise rules, automerge defaults — lives there. Each repository carries a small `renovate.json` holding only what is specific to its stack.

*Alternative considered:* a dedicated `renovate-config` repository (also auto-detected). Rejected because `.github` already exists, is already Pulumi-managed, and already serves this exact role for `claude-review.yml`. A second configuration repository would split the same concern across two places.

### D3: Grouping by version-coupled family

The `dependency-update-automation` spec requires that version-coupled sets move as a unit. The concrete groups, derived from inspecting the manifests:

| Group | Members | Automerge |
|---|---|---|
| `otel-go` | `go.opentelemetry.io/otel{,/metric,/sdk,/trace}`, both OTLP exporters, `contrib/.../otelgrpc`, `contrib/.../otelhttp` | yes |
| `connectrpc-go` | `connectrpc.com/{connect,authn,cors,grpchealth,otelconnect,validate}` | yes |
| `go-tools` | `tool` directive entries: buf, delve, mockery, gofumpt | yes |
| `aurelia` | `aurelia`, `@aurelia/{i18n,router,testing,vite-plugin,storybook}` | yes, incl. RC→GA |
| `vitest` | `vitest`, `@vitest/{browser,browser-playwright,coverage-v8,ui}` | yes |
| `storybook` | `storybook`, `@storybook/{addon-a11y,addon-docs,addon-vitest,builder-vite}` | yes |
| `vite` | `vite`, `vite-plugin-node-polyfills`, `vite-plugin-pwa` | yes |
| `otel-js` | the five `@opentelemetry/*` packages | yes |
| `connectrpc-js` | `@connectrpc/connect{,-web}`, `@bufbuild/protobuf` | yes |
| `stylelint` | `stylelint` and its four config/plugin packages | yes |
| `workbox` | the four `workbox-*` packages across `dependencies` and `devDependencies` | yes |
| `pulumi` | `@pulumi/*`, `@pulumiverse/zitadel` | only on an empty preview |

Core-versus-contrib version skew (OpenTelemetry Go pairs `v1.44.x` core with `v0.6x` contrib) is why these are grouped by family rather than by matching version number.

`@biomejs/biome` is pinned to the same exact version in `frontend` and `cloud-provisioning`. Renovate cannot group across repositories, so the two are placed on the same schedule; they will be proposed as two PRs that land close together. Accepting brief skew is cheaper than the alternatives (a shared config package, or a custom cross-repo bump workflow) for a formatter.

### D4: Custom managers for the three version fan-outs

Go (8 locations), Node (14 locations), and Playwright (3 locations) are each bound into one Renovate group using regex custom managers over the workflow YAML, `.golangci.yml`, Dockerfiles, and `AGENTS.md`, combined with the native `gomod` / `npm` / `dockerfile` managers.

The Go unit must include `go.mod`'s `go` language directive alongside `toolchain`. Renovate's `gomod` manager treats the two as separate dependencies and will propose the `go` directive on its own, which is precisely the partial update the binding exists to prevent.

This is the load-bearing decision of the change. Without it, a lone `go.mod` `toolchain` bump produces a PR whose CI installs Go 1.27 via `setup-go`, then silently builds with the proposed toolchain because `GOTOOLCHAIN` defaults to `auto` — a green result that verified a configuration nobody proposed.

*Alternative considered:* deriving every location from a single source (`setup-go` supports `go-version-file: go.mod`; Dockerfiles could take a build arg). This is the better end state and removes the need for custom managers on the Go axis. It is deliberately not bundled here: it changes how CI resolves its toolchain, which is exactly the mechanism this change needs to be able to trust while it is being established. Recorded as follow-up work in `tasks.md`.

### D5: `@playwright/test` pinned exactly

`"@playwright/test": "^1.49.1"` currently resolves to 1.58.1 while `ci.yaml` hard-pins `mcr.microsoft.com/playwright:v1.58.1-noble`. The caret lets the two drift apart with no PR at all. Pinning exactly makes every Playwright move an explicit, reviewable PR that updates the package and the container tag together.

The unit has a third member: `frontend/AGENTS.md` documents the baseline-regeneration command with the same image tag. That tag is the "baseline-generation image" the CI comment names, so if the documented command drifts from the CI job, a human following the documentation regenerates baselines against a different renderer than the one that validates them — silently poisoning the committed PNGs. It is bound into the same group.

Playwright is excluded from automerge because a version bump changes Chromium's rendering and therefore invalidates the committed `toMatchScreenshot` baselines, which Renovate cannot regenerate. Grouping makes the failure honest — CI goes red, so automerge correctly declines — but a human must regenerate baselines to advance the PR. The `storybook-component-testing` spec already defines baseline adoption as a human action; this preserves that.

### D6: Pulumi preview as a distinct CI signal

`cloud-provisioning` CI runs `make lint-ts` (biome + `tsc --noEmit`) only; `make check` also runs `vitest`, but CI never invokes it. Both gaps are closed: a `test` job, and a `pulumi-preview` job.

The preview job runs `pulumi preview --diff` against the prod stack. The command itself is established practice — it is documented across seven runbooks and the repository's own pull request template already instructs reviewers to "check the CI/GitHub Actions output for the Preview result. If CI is not running, paste the local `pulumi preview` output here." CI was always the intended home for it; only the wiring is missing.

What CI already has: `WORKLOAD_IDENTITY_PROVIDER` and `SERVICE_ACCOUNT` are repository variables, so GCP authentication through `google-github-actions/auth@v2` works today. What it lacks is a `PULUMI_ACCESS_TOKEN`. That single secret is sufficient for the rest, because `Pulumi.prod.yaml` opens with `environment: liverty-music/prod` — ESC resolves the Cloudflare, Zitadel and GitHub provider credentials at stack load. The credential surface is therefore one new secret, not four.

That token is not read-only: it can reach the stack's state and, with ESC, write-capable provider credentials. The safety property is not credential scope but the operation — `preview` computes a plan and never applies one. Two constraints preserve it: the job runs on `pull_request` (never `pull_request_target`), so a fork PR cannot execute repository code with these secrets; and no `pulumi up` path exists in this workflow.

Pulumi automerge is then conditional on the preview reporting no resource changes, which is what makes "CI green" a truthful statement for a provider upgrade. This is the stricter of the two options considered during exploration; the weaker option (never automerge Pulumi) was rejected because the operator's policy is that a green pipeline is sufficient authority, and the honest way to honour that is to make the pipeline actually check.

### D7: Schema SDK exclusion is visible, not silent

`buf.build/gen/go/liverty-music/schema/*` and `@buf/liverty-music_schema.*` are set to `enabled: false` rather than added to `ignoreDeps`. Both suppress PRs, but `enabled: false` keeps the dependency listed on the dependency dashboard as disabled-with-an-update-available. That turns the exclusion into a drift detector: a schema release whose consumers were never advanced becomes visible instead of invisible.

`buf.build/gen/go/pocketsign/apis/*` is *not* excluded — it is a third-party schema on someone else's release cadence, where falling behind is the risk rather than the safeguard.

Renovate needs `hostRules` credentials for `buf.build/gen/npm/v1/` to read `@buf` package metadata at all. Those are still required even though the liverty-music packages are disabled, because the datasource is consulted to populate the dashboard.

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

## Risks / Trade-offs

- **A custom manager's regex silently stops matching** after a workflow is reformatted, so one location of a fan-out is quietly left behind — the exact failure the grouping exists to prevent. → Add an assertion that fails CI when the Go-version locations disagree with `go.mod`, so drift is caught by the pipeline rather than by a regex that matched nothing.
- **Automerge lands a green-but-wrong change** in an area CI does not observe. The audit found three such areas; two are closed here (WebKit, Pulumi preview) and one is not: `workbox` and `vite-plugin-pwa` remain automerged while the PWA offline-cache and install-prompt specs stay excluded from CI as unavailable in headless runs. → Accepted knowingly and recorded in the spec as a known gap rather than assumed coverage; PWA behavior is confirmed manually before release.
- **Grouped PRs are harder to bisect.** A ten-package OpenTelemetry PR that breaks a test gives a coarser signal than ten separate PRs. → Accepted: the packages cannot be upgraded separately anyway, so the finer signal was never actually available.
- **A Pulumi token reaching PR CI resolves write-capable provider credentials through ESC** (D6). → Mitigated by operation rather than scope: the workflow contains no apply path, and it triggers on `pull_request` rather than `pull_request_target`, so fork code never runs with the secret. Residual risk is a malicious commit pushed directly to a branch in the repository, which already implies write access.
- **Renovate's own configuration is unversioned policy.** A careless edit to the org preset silently changes behavior in four repositories. → It lives in a Pulumi-managed repository under the same review requirements as any other change.

## Migration Plan

1. **Land the CI hardening first** — WebKit projects, `cloud-provisioning` test and preview jobs, `@playwright/test` exact pin — and confirm `CI Success` still passes on an unrelated PR in each repository. Nothing about update automation is enabled yet, so this stage is reversible by reverting the workflow files.
2. **Install Renovate with automerge globally off.** Let the dependency dashboard populate and one full weekly cycle run. This reveals actual PR volume and catches custom-manager regexes that match nothing, without any merge risk.
3. **Enable `allowAutoMerge` in Pulumi and turn automerge on by group**, starting with `devDependencies` and GitHub Actions, then the coupled families, then the Go and Node version groups.
4. **Rollback**: at any stage, setting automerge off in the org preset stops unattended merges across all four repositories in one commit, leaving PR creation intact.

## Open Questions

- Whether the two `it.skip` cases in `frontend/test/app-shell.spec.ts` (landing-page render, layout structure) should be repaired as part of stage 1. They cover the application shell, which is exactly what an automerged Aurelia GA upgrade would most plausibly break — but they are independent of the automation machinery, so the answer does not change the specs or the task breakdown.
- Whether the `specification` repository needs grouping rules at all beyond the inherited preset. Its dependency axes are GitHub Actions, mise, pre-commit hooks and `buf.lock`, all covered by the org preset; a repository-local `renovate.json` may turn out to be unnecessary.
- Whether `.github` should eventually get its own CI and branch protection so it can participate in automerge like the other four (D11).
