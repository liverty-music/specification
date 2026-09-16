## 1. Dead-pin cleanup

- [ ] 1.1 In `frontend`, land the already-staged removal of `overrides.bfj` on a branch (it is currently uncommitted on `main`). Verify `npm ci` reports no lockfile change and `npm audit --omit=dev --audit-level=moderate` reports 0 vulnerabilities.
- [ ] 1.2 In `frontend`, attempt removal of `overrides.minimatch`: delete the entry, regenerate `package-lock.json` on Node 22 (matching CI), and confirm `filelist` resolves without introducing an advisory. If `filelist`'s declared `^5.0.1` now resolves to a version that breaks the build or trips the audit, keep the override and record why in a comment on the lockfile-adjacent PR description instead.
- [ ] 1.3 Verify the top-level `liverty-music/e2e/` husk is gone and that `frontend/e2e/` is untouched (deleted during exploration; confirm no tooling referenced the old path).

## 2. CI hardening — WebKit coverage

- [ ] 2.1 Add `--project=webkit-repro --project=chromium-control` to the `e2e` job in `frontend/.github/workflows/ci.yaml`. The job already installs both `chromium` and `webkit`, so no new browser install step is needed.
- [ ] 2.2 Confirm `page-help-sheet-webkit.spec.ts` now executes in CI and that the bottom-sheet regression guard it encodes passes.
- [ ] 2.3 Audit every project in `playwright.config.mjs` against the `ci-optimization` requirement that each is either executed or documented as unrunnable. `authenticated` needs a `storageState` CI has no way to produce — record the reason at the project.
- [ ] 2.4 Audit at SPEC granularity, not just project granularity. `pwa-offline-cache.spec.ts` and `pwa-install-prompt.spec.ts` are specs inside the `pwa` project's `testIgnore`, not projects of their own, so a project-level audit misses them entirely. Enumerate every spec matched by no executed project, confirm each carries its reason, and publish the resulting list as the known-gaps set that design Risk 2 refers to.

## 3. CI hardening — cloud-provisioning verification

- [ ] 3.1 Add a `test` job to `cloud-provisioning/.github/workflows/ci.yml` running the repository's `vitest` suite, with its matching `test-skip` job, and add both to `ci-success`'s `needs` and `allowed-skips`.
- [ ] 3.1a Extend the `changes` paths-filter in that workflow to include `Pulumi.yaml` and `Pulumi.*.yaml`. Without them a PR that only edits stack configuration skips every job and still reports `CI Success` green, violating the "preview on every pull request" requirement.
- [ ] 3.2 Add a `PULUMI_ACCESS_TOKEN` secret to `cloud-provisioning` via Pulumi-managed repository secrets. This is the only new credential: GCP already authenticates through the existing `WORKLOAD_IDENTITY_PROVIDER` / `SERVICE_ACCOUNT` repository variables, and `Pulumi.prod.yaml`'s `environment: liverty-music/prod` makes ESC resolve the Cloudflare, Zitadel and GitHub provider credentials at stack load (design D6).
- [ ] 3.3 Add a `pulumi-preview` job running `pulumi preview --diff` against the prod stack, with its matching `pulumi-preview-skip` job, wired into `ci-success` / `allowed-skips`. The job MUST trigger on `pull_request`, never `pull_request_target`, so fork code cannot execute with the token. Confirm the workflow contains no `pulumi up` path.
- [ ] 3.3a Update `.github/pull_request_template.md`: its Pulumi Preview section already says "check the CI/GitHub Actions output ... If CI is not running, paste the local output". Once CI runs preview on every PR, drop the local-paste fallback so the checklist stops implying preview is optional.
- [ ] 3.4 Make the preview's "no resource changes" outcome a distinct, machine-readable signal (job output or separate check) so an automerge decision can depend on it.
- [ ] 3.5 Verify on a no-op PR that the preview reports zero changes, and on a deliberately resource-altering PR that it reports the change and marks the PR ineligible for automerge.

## 4. CI hardening — Playwright lockstep

- [ ] 4.1 Change `frontend/package.json` `@playwright/test` from `^1.49.1` to the exact currently-resolved version (`1.58.1`) and regenerate the lockfile on Node 22.
- [ ] 4.2 Confirm the value matches the `mcr.microsoft.com/playwright:v1.58.1-noble` container tag in `ci.yaml`, and that `npm ci` plus the Storybook component tests still pass against the committed baselines.

## 5. Renovate — organization preset

- [ ] 5.1 Create `liverty-music/.github/renovate-config.json` holding shared policy: schedule (weekly Saturday JST groups, monthly groups at month start), `prConcurrentLimit`, vulnerability updates exempt from schedule, `dependencyDashboard: true`, and **`automerge` globally off** for now.
- [ ] 5.1a In the org preset, disable automerge for the `.github` repository specifically and permanently (design D11). `.github` has no `GitHubRepositoryComponent`, so no branch protection and no `CI Success` gate exist there — an automerge would land with no gate at all. Renovate still raises PRs for its GitHub Actions.
- [ ] 5.1b Set Renovate to rebase its pull requests when the base branch moves, so `cloud-provisioning`'s `requireUpToDateBranch: true` does not deadlock the automerge queue (design D13). Do NOT remove that flag — it prevents a documented class of Pulumi resource-deletion accident.
- [ ] 5.2 Add shared cross-repository manager rules to the preset: GitHub Actions, Docker base images, mise tools, pre-commit hook revisions (`specification/.pre-commit-config.yaml`), `buf.lock` module dependencies, and kustomize image tags (`backend/k8s/**`).
- [ ] 5.2a Pin the mise tools to concrete versions first. `cloud-provisioning/.mise.toml` declares `kustomize = "latest"` and `specification/.mise/config.toml` declares `buf = "latest"` and `pre-commit = "latest"`; a floating reference can never produce an update proposal, so the mise axis would be silently inert and task 8.2 would misread that as "no updates available".
- [ ] 5.3 Add `hostRules` credentials for the `buf.build/gen/npm/v1/` registry so `@buf` package metadata is readable.
- [ ] 5.4 Install the Mend-hosted Renovate GitHub App on the `liverty-music` organization and confirm each repository resolves the preset (the onboarding PR should show `local>liverty-music/.github:renovate-config` in its inherited config).

## 6. Renovate — per-repository configuration

- [ ] 6.1 `backend/renovate.json`: extend the org preset; add the `otel-go`, `connectrpc-go`, and `go-tools` groups per design D3; set `constraintsFiltering: strict`; leave `// indirect` dependencies unmanaged.
- [ ] 6.2 `backend/renovate.json`: disable `buf.build/gen/go/liverty-music/schema/*` via `enabled: false` (not `ignoreDeps`, per design D7) so it stays visible on the dashboard. Leave `buf.build/gen/go/pocketsign/apis/*` enabled.
- [ ] 6.3 `frontend/renovate.json`: extend the org preset; add the `aurelia`, `vitest`, `storybook`, `vite`, `otel-js`, `connectrpc-js`, `stylelint`, and `workbox` groups per design D3.
- [ ] 6.4 `frontend/renovate.json`: disable `@buf/liverty-music_schema.*` via `enabled: false`; exclude `@playwright/test` and all `overrides` entries from automerge.
- [ ] 6.5 `cloud-provisioning/renovate.json`: extend the org preset; add the `pulumi` group, excluded from automerge pending the preview signal from 3.4.
- [ ] 6.6 Place `@biomejs/biome` on the same schedule in `frontend` and `cloud-provisioning` so the two exact pins are proposed together (design D3 — cross-repo grouping is not possible).
- [ ] 6.7 Decide whether `specification` needs a repository-local `renovate.json` at all, or whether the inherited preset covers its GitHub Actions and mise axes (design Open Question 2). Create it only if needed.

## 7. Renovate — version fan-out custom managers

- [ ] 7.1 Add a `customManagers` entry grouping all eight Go-version locations: `go.mod`'s `go` language directive AND its `toolchain` directive, the `Dockerfile` `golang:` tag, `.golangci.yml` `go:`, and the four `go-version:` workflow inputs. The `go` directive must be included explicitly — Renovate's `gomod` manager treats it as a separate dependency and will otherwise propose it alone. Verify a dry run proposes all eight together.
- [ ] 7.2 Add a CI assertion in `backend` that fails when the eight Go-version locations disagree, so a regex that silently stops matching is caught by the pipeline (design Risk 1).
- [ ] 7.3 Add a `customManagers` entry grouping all fourteen Node-version locations across `frontend` and `cloud-provisioning`: eight `node-version:` workflow inputs, three `node:` Dockerfile tags, `cloud-provisioning`'s `engines.node`, and the `@types/node` major in both manifests. `@types/node` is part of the unit — a Node runtime bump without it leaves the type definitions describing the previous runtime.
- [ ] 7.4 Add a `customManagers` entry binding `@playwright/test` to the `mcr.microsoft.com/playwright` container tag in `ci.yaml` AND to the same tag in the baseline-regeneration command documented in `frontend/AGENTS.md`. All three move together, grouped and automerge-disabled.

## 8. Observation phase

- [ ] 8.1 Let one full weekly cycle run with automerge still globally off. Record actual PR count per group against the ~36/month estimate in design D10.
- [ ] 8.2 Verify each custom manager from section 7 actually matched: confirm at least one proposed PR (or dashboard entry) touches every location in each fan-out. A group that proposed nothing indicates a non-matching regex, not an up-to-date dependency.
- [ ] 8.3 Confirm the disabled schema SDKs appear on the dependency dashboard as disabled-with-update-available, so the drift-detection behavior required by the spec is working.
- [ ] 8.4 Adjust grouping based on observed volume before enabling any automerge.

## 9. Enable automerge

- [ ] 9.1 Add `allowAutoMerge: true` to `defaultRepositoryArgs` in `cloud-provisioning/src/github/components/organization.ts`. Note this reaches all five repositories including `.github`; the gate against unattended merges there is the Renovate-side exclusion from 5.1a, since `.github` has no branch protection to rely on. Confirm `requiredStatusCheckContexts` stays `['CI Success']` on the other four and that the enabled merge strategy remains merge-commit-only (`allowSquashMerge` and `allowRebaseMerge` are both false).
- [ ] 9.2 Run `pulumi up -s prod` and verify the setting is live on all participating repositories.
- [ ] 9.3 Enable automerge for the lowest-risk groups first: `devDependencies`, GitHub Actions, Docker digests, mise. Observe one cycle.
- [ ] 9.4 Enable automerge for the coupled families: `otel-go`, `connectrpc-go`, `go-tools`, `vitest`, `storybook`, `vite`, `otel-js`, `connectrpc-js`, `stylelint`, `workbox`, `aurelia` (including the RC→GA transition), plus `typescript`, `biome`, the `pannpers/*` libraries, `stripe-go`, `zitadel/*`, and the `pocketsign` schema SDK.
- [ ] 9.5 Enable automerge for the Go-version and Node-version groups, patch-level only at first. Expect such a PR to leave `golang:1.27-alpine`, `go: '1.27'`, `node:22-alpine` and `engines.node` untouched — those record coarser precision and are already satisfied (design D12). Verify this reads as complete rather than partial in the custom manager's output.
- [ ] 9.6 Enable conditional automerge for the `pulumi` group, gated on the empty-preview signal from 3.4. Confirm a rebase triggered by `requireUpToDateBranch` re-runs the preview rather than reusing the previous result.
- [ ] 9.7 Verify the rollback path: setting automerge off in the org preset stops unattended merges across all four repositories in one commit, with PR creation still running.

## 10. Documentation

- [ ] 10.1 Reword the `toolchain` comment in `backend/go.mod` as a floor-and-history record (design D8): keep the nine `GO-2026-*` advisories as the reason the floor was set, and note that the directive is advanced automatically. Its claim must stay true after a bump.
- [ ] 10.2 Document the `overrides` exit conditions in `frontend` — `fflate` and `dompurify` are removed, not upgraded, once `posthog-js` widens its ranges (design D9) — so a future reader does not mistake the exact `fflate` pin for neglect.
- [ ] 10.3 Add a short runbook covering the two recurring human actions: regenerating Storybook visual baselines after a `@playwright/test` bump, and reviewing a Pulumi preview that reports changes.

## 11. Follow-ups (not required for this change)

- [ ] 11.1 Replace the Go-version custom manager with single-source derivation: `setup-go` reading `go-version-file: go.mod`, and the Dockerfile taking a build arg. Deferred from design D4 because it changes how CI resolves its toolchain while this change is establishing trust in that mechanism.
- [ ] 11.2 Decide whether to repair the two `it.skip` cases in `frontend/test/app-shell.spec.ts` (design Open Question 1). They cover the application shell — the surface an automerged Aurelia GA upgrade is most likely to break.
- [ ] 11.3 Reassess whether `workbox` and `vite-plugin-pwa` should stay automerged given that the PWA offline-cache and install-prompt specs remain outside CI (design Risk 2).
- [ ] 11.4 Decide whether `.github` should get its own CI and branch protection so it can participate in automerge like the other four (design D11).
