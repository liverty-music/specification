## Why

Dependency updates across the four liverty-music repositories are entirely manual today — there is no Renovate or Dependabot configuration anywhere. Twelve distinct dependency axes (Go modules, Go `tool` directives, the Go toolchain, npm packages, npm `overrides`, GitHub Actions, Docker base images, mise tools, Pulumi providers, pre-commit hook revisions, `buf.lock` module dependencies, and kustomize image tags) are each bumped by hand, so security patches land only when someone notices them.

The repositories are already well positioned for automation: every workflow terminates in a `CI Success` gate job (`re-actors/alls-green`), and branch protection already requires exactly that check. The blocker is not the gate — it is that `CI Success` currently certifies less than it appears to. An audit found four CI coverage gaps and three version-fan-out hazards that would make "green means safe" false for automerged PRs. This change closes those gaps first, then introduces Renovate with an automerge policy that the CI can actually honour.

## What Changes

### Close the CI coverage gaps that automerge would rely on

- **WebKit is never exercised in CI.** `playwright.config.mjs` defines `webkit-repro` (iPhone 14 / WebKit) and `chromium-control` projects, but the `e2e` job runs only `--project=functional --project=pwa` and the `smoke` job only `--project=smoke --project=onboarding`. Neither WebKit project is invoked anywhere. Worse, the `functional` project's `testIgnore` excludes `page-help-sheet-webkit.spec.ts` on the stated grounds that it is "Covered by webkit-repro / chromium-control projects" — so that spec has **zero** CI coverage, and the bottom-sheet regression guard it encodes is inert.
- **Pulumi changes are never previewed.** `cloud-provisioning`'s CI runs `make lint-ts` (biome + `tsc --noEmit`) only. A provider upgrade that would replace live GCP resources passes a type check without complaint.
- **`cloud-provisioning` never runs its tests.** `package.json` defines a `test` script and `make check` is `lint-ts test`, but CI invokes `make lint-ts`, so `vitest` never executes on a PR.
- **The `pwa` project ran zero specs.** `e2e/pwa/` holds exactly three specs and all three sat in the project's `testIgnore`, so `--project=pwa` matched nothing. CI has been starting an empty project and counting it as a pass, leaving `workbox` and `vite-plugin-pwa` entirely unverified while appearing covered.

  Re-verification confirmed the recorded exclusion reason for `pwa-offline-cache.spec.ts` ("not available in CI headless") was wrong — `context.setOffline()` works fine headless — but the real obstacle was different and larger: `vite.config.ts` sets vite-plugin-pwa's `devOptions.enabled: false` and the e2e web server is the dev server, so no service worker existed in the environment the spec ran against. Removing the exclusion alone would not have closed the gap. The PWA specs are moved to their own config running against a production preview build, and the spec's assertions are rewritten — it previously asserted only that the page was non-blank, which passes when no service worker was ever registered and so could never have caught a workbox regression. This is what lets `workbox` be automerged honestly rather than nominally.
- **Two skipped app-shell tests.** `frontend/test/app-shell.spec.ts` skips the landing-page render and layout-structure assertions — the surface an Aurelia upgrade would most plausibly break. They are repaired here, and Aurelia automerge is gated on them.

### Bind each version fan-out into a single reviewable unit

Three logical versions are each spread across multiple files, so a bot bumping one location produces a PR whose green CI is meaningless:

- **Go — 8 locations.** `backend/go.mod` carries both the `go 1.27` language directive and `toolchain go1.27.0`; `backend/Dockerfile` has `golang:1.27-alpine`; `backend/.golangci.yml` has `go: '1.27'`; and four `go-version: "1.27.0"` entries span `test.yml` and `lint.yml`. Because `GOTOOLCHAIN` defaults to `auto`, a lone `go.mod` bump makes CI silently build with a toolchain it did not install. The `go` directive matters separately: Renovate's `gomod` manager can propose it on its own, producing exactly the partial update this binding exists to prevent.
- **Node — 14 locations.** Eight `node-version: '22'` workflow inputs, three `FROM node:22-alpine` lines, `cloud-provisioning`'s `engines.node`, and the `@types/node` major in both `frontend` and `cloud-provisioning`.
- **Playwright — 3 locations, one of them floating.** `package.json` pins `"@playwright/test": "^1.49.1"` (resolving to 1.58.1); `ci.yaml` hard-pins the component-test container to `mcr.microsoft.com/playwright:v1.58.1-noble`; and `frontend/AGENTS.md` documents baseline regeneration with that same image tag, which is the "baseline-generation image" the CI comment requires all three to stay in lockstep with. A caret bump desynchronises them and invalidates every committed `toMatchScreenshot` baseline — which Renovate cannot regenerate, producing a permanently red, un-advanceable PR.

### Introduce Renovate

- An organization-level configuration at `liverty-music/.github/renovate-config.json` **extending Renovate's maintained `config:best-practices` preset**, with a per-repository `renovate.json` in `backend`, `frontend`, `cloud-provisioning`, and `specification` adding only what is specific to each stack.
- **A release-age delay before any update is proposed.** Automerge removes the interval in which a human would ordinarily notice a compromised release; published analyses put most supply-chain windows of opportunity under a week, so a delay of a few days intercepts the majority. Inherited from the preset and configured explicitly so it survives a schedule change.
- **SHA pinning for third-party GitHub Actions.** 105 `uses:` references across 21 workflows in five repositories are pinned to mutable tags today, meaning each action's owner can change what runs in workflows holding GCP, ci-bot and Pulumi credentials. Exactly one reference is SHA-pinned already, so the practice is understood here but unapplied. Renovate raises the pinning PRs itself.
- Grouping of version-coupled families into single PRs, reducing an estimated ~100 PRs/month to ~36. Most families (Storybook, Vitest, OpenTelemetry JS, stylelint, Pulumi) are grouped by maintained upstream presets; local rules are written only for the four with no upstream coverage — OpenTelemetry Go, Connect-RPC Go, the Go `tool` entries, and Aurelia.
- Automerge for minor and patch updates whose risk the CI genuinely covers, per the operator's stated policy that a green pipeline is sufficient authority to merge. This includes the Aurelia `2.0.0-rc.2` → `2.0.0` GA transition and the `pocketsign` schema SDK.
- **Withholding from automerge only where a reviewer can see what the pipeline cannot** — an infrastructure provider update whose preview the reviewer runs themselves, a Playwright bump needing baseline regeneration, an `overrides` entry needing a removal judgement. Where no reviewer could evaluate the risk, the pipeline is extended instead: routing a version-and-lock-file diff through a person produces ceremony, not verification. This is why the two PWA-adjacent gaps and the skipped app-shell tests are repaired rather than routed around.
- **Infrastructure credentials are kept off automated pull requests.** Producing a Pulumi preview means installing the stack's dependencies and executing its program, and the stack resolves production credentials from a shared ESC environment that cannot be narrowed per job. Since Renovate pushes to branches inside the repository, previewing a dependency bump would execute a just-published third-party package with those credentials before anyone read it. The preview runs only on member-authored pull requests, and provider updates are reviewed rather than automerged.
- **Renovate is disabled for `buf.build/gen/go/liverty-music/schema/*` and `@buf/liverty-music_schema.*`.** These are not dependency updates: every historical bump was an explicit task inside an OpenSpec change that also migrated the consuming code. Letting Renovate bump the repositories independently would open a schema-skew window and leave the code migration undone. They remain visible on the dependency dashboard as drift detection.

  That drift is not hypothetical. The three consumers are already on three different schema builds — `frontend` on `20260913052028-ce6e594ac619`, `backend`'s `connectrpc/go` on `20260913101508-7795859df477`, and its `protocolbuffers/go` on `20260915050914-c470358dd62d` — which the `dependency-update-automation` capability requires to be one build. Nothing reports this today, which is the argument for `enabled: false` over `ignoreDeps`: the dashboard is what makes an un-advanced consumer visible. Resolving the existing skew is out of scope here (this change bumps nothing); the dashboard this change turns on is what will surface it.

### Retire dead dependency pins

- `frontend`'s `overrides.bfj` is dead: it entered via the snarkjs-based ZKP feature (commit `a0942ca2`), which was removed by the `remove-blockchain-ticket-system` change. `bfj` no longer appears in the lockfile at all. *(Already removed in the working tree; the lockfile was unaffected.)*
- `overrides.minimatch` has likewise outlived its origin, but is **not** inert: `filelist@1.0.4` declares `minimatch: ^5.0.1`, and the override forces that transitive resolution to 10.2.4 — five majors above what `filelist` asks for. Removing it changes resolution, so it needs a lockfile regeneration and verification rather than a deletion.
- `overrides.fflate` (`0.4.9`, exact) and `overrides.dompurify` (`^3.4.13`) are both live security pins driven by `posthog-js`, which caps `fflate` at `^0.4.8`. Their correct exit condition is removal once `posthog-js` widens its range — an action Renovate cannot perform. Keeping `posthog-js` itself current is the root-cause remedy.

## Capabilities

### New Capabilities

- `dependency-update-automation`: How Renovate is configured across the four repositories — the organization preset and its inheritance, grouping of version-coupled package families, the automerge policy and its exclusions, the version fan-outs that must be updated as single units, and the dependencies that are deliberately withheld from automation.

### Modified Capabilities

- `ci-optimization`: Adds requirements that the frontend CI exercise the WebKit engine, that `cloud-provisioning` CI run `pulumi preview` and its test suite, and that repositories participating in automerge have it enabled through Pulumi-managed repository configuration.

## Impact

**Repositories**: `liverty-music/.github` (new org preset), `backend`, `frontend`, `cloud-provisioning`, `specification`.

**Files**

- New: `liverty-music/.github/renovate-config.json`; `renovate.json` in each of the four repositories.
- `frontend/.github/workflows/ci.yaml` — WebKit projects added to the `e2e` job; a "Run PWA tests" step invoking the new PWA config; Playwright container tag bound to `@playwright/test`.
- New: `frontend/playwright.pwa.config.mjs` — PWA/service-worker specs run from their own config against `vite preview` over a production build, following the existing `playwright.smoke.config.mjs` precedent so the build does not slow every other e2e run.
- New: `frontend/docs/ci-coverage-gaps.md` — the enumerated known-gaps set, maintained at spec granularity with a named control per gap.
- `frontend/playwright.config.mjs` — the `pwa` project moves out to the new config; the `authenticated` project records why CI cannot run it; two `testIgnore`/`testMatch` entries naming specs deleted in `c83dc23` removed.
- `frontend/package.json` — `preview` and `test:pwa` scripts added.
- **All 21 workflow files across the five repositories** — third-party `uses:` references pinned to commit SHAs. Generated by Renovate, reviewed and merged per repository.
- `frontend/package.json` — `@playwright/test` changed from `^1.49.1` to an exact pin; `overrides.bfj` removed.
- `cloud-provisioning/.github/workflows/ci.yml` — new `pulumi-preview` job (member-authored PRs only) and a test job, both wired into `ci-success` / `allowed-skips`; `Pulumi*.yaml` added to the paths filter.
- `frontend/test/app-shell.spec.ts` — two skipped tests repaired.
- `cloud-provisioning/src/github/components/organization.ts` — `allowAutoMerge` added to `defaultRepositoryArgs`. This is a `github.Repository` argument, so it cannot be set from `GitHubRepositoryComponent` (which manages protection, environments, variables and secrets, not the repository resource itself).
- `backend/go.mod`, `backend/Dockerfile`, `backend/.golangci.yml`, `backend/.github/workflows/{test,lint}.yml` — unchanged in value, but brought under a Renovate `customManager` so the eight Go-version locations move together.

**Infrastructure**: GCP authentication from the PR context already works through the existing `WORKLOAD_IDENTITY_PROVIDER` / `SERVICE_ACCOUNT` repository variables, so no new IAM role or Workload Identity binding is needed. The only new credential is a `PULUMI_ACCESS_TOKEN` secret; `Pulumi.prod.yaml`'s `environment: liverty-music/prod` makes ESC resolve the Cloudflare, Zitadel and GitHub provider credentials from there. Because that token cannot be narrowed per job, the preview is withheld from automated dependency pull requests rather than run with reduced privileges.

**Operational**: Merge volume shifts from a manual queue of roughly 100 PRs/month to roughly 36 grouped PRs/month, of which about 30 merge without human review. The residual human-reviewed set is majors, Pulumi previews that report a diff, `@playwright/test` bumps requiring baseline regeneration, and `overrides` removals.

**Explicitly out of scope**: covering `pwa-install-prompt.spec.ts`, which depends on browser install heuristics headless CI cannot trigger; it remains an enumerated gap constraining `vite-plugin-pwa` manifest behavior. Also out of scope: AI-assisted triage of Renovate PRs. At roughly two human-reviewed PRs per week, the existing `claude-code-review.yml` is sufficient; a dedicated triage layer is not justified at this volume.

**Assumption**: CI hardening and Renovate introduction are bundled as one change because the hardening exists solely to make the automerge policy sound — shipping Renovate first would enable automerge against a pipeline that does not yet verify what the policy assumes. If the hardening turns out to be large enough to warrant its own review cycle, it can be split into a `harden-ci-for-automerge` predecessor without reworking the Renovate configuration.
