## 1. Specification (this change)

- [x] 1.1 Open PR in `specification` with the `prod-image-pipeline` delta (proposal/design/specs/tasks); pass `buf-pr-checks.yml` and review. No proto change → no BSR/Release needed.
- [x] 1.2 All implementation PRs merged (backend #315, frontend #377, cloud-prov #321) and §5 verified; running the openspec sync + archive for this change.

## 2. Backend pipeline (`backend/.github/workflows/deploy.yml`)

- [x] 2.1 Remove `paths:` from the `push` trigger so every push to `main` starts the workflow (keep `release: [published]`).
- [x] 2.2 Add a build-vs-inherit decision step: compute changed files over `${{ github.event.before }}..${{ github.sha }}` and match against the build glob set (`**.go`, `go.mod`, `go.sum`, `Dockerfile`, `.github/workflows/deploy.yml`); expose a boolean output (`build` vs `inherit`).
- [x] 2.3 Gate the existing build-and-push steps on the `build` decision (push-event only), preserving `:latest,:main,:<sha>` to dev AR for all 4 matrix images.
- [x] 2.4 Add the inherit path (push-event + `inherit` decision): per matrix image, resolve the dev-AR digest of `<image>:${{ github.event.before }}` and `crane copy` it to `<image>:${{ github.sha }}`, then re-point `:main` and `:latest`; no `docker build`.
- [x] 2.5 Route force-push (`github.event.forced`) and branch-creation (`github.event.created` / zero `before`) to the BUILD path — never inherit from an orphaned/non-ancestor tip. The inherit path resolves **only** `<image>:${{ github.event.before }}` (NO `:main`/`HEAD^1` fallback — those can pin non-equivalent bytes when the chain has a gap), classifies the resolve failure like the release path (auth → fail fast; transient → bounded retry; `NOT_FOUND` → fail loud with a seed-and-re-cut message), and never writes `:<sha>` at a wrong digest.
- [x] 2.6 Update the release `Resolve dev AR digest` final error message and the `Verify release commit is on main` message: drop the "filtered-out / non-main commit" attribution and the "re-target to an earlier commit" / "main HEAD only" wording; state the invariant (a `main` HEAD always resolves; missing `:<sha>` means in-flight or a failed build/inherit). Keep the 6×60s retry.
- [x] 2.7 Confirm the job's `concurrency` block is `group: <workflow>-<ref>`, `cancel-in-progress: false` (serializes consecutive `main` pushes → preserves the inherit chain), and use `set -euo pipefail` in the inherit step's `crane copy` sequence.

## 3. Frontend pipeline (`frontend/.github/workflows/push-image.yaml`)

- [x] 3.1 Remove `paths:` from the `push` trigger (keep `release: [published]` and existing `workflow_dispatch`).
- [x] 3.2 Add the build-vs-inherit decision over `${{ github.event.before }}..${{ github.sha }}` against the frontend build glob set (`src/**`, `public/**`, `scripts/**`, `package.json`, `package-lock.json`, `vite.config.ts`, `Dockerfile`, `Caddyfile`, `.github/workflows/push-image.yaml`).
- [x] 3.3 Gate the existing build-and-push (incl. the `verify:build-templates` assertion) on the `build` decision.
- [x] 3.4 Add the inherit path for `web-app`: resolve `web-app:${{ github.event.before }}` digest and `crane copy` to `web-app:${{ github.sha }}`, re-point `:main`/`:latest`; no build; force-push/branch-creation → BUILD; resolve `:<before>` only with classified retry and NO tag fallback (same rules as 2.5).
- [x] 3.5 Update the release digest-resolve error message symmetrically with task 2.6.
- [x] 3.6 Confirm the `concurrency` block (`group: <workflow>-<ref>`, `cancel-in-progress: false`) is present, and use `set -euo pipefail` in the inherit step's `crane copy` sequence.

## 4. Runbook (`cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md`)

- [x] 4.1 Revise the "Failure: dev AR `:<sha>` does not exist" section: remove the path-filter cause (now eliminated); state remaining causes are in-flight race or a failed build/inherit job; recovery is "re-run the build/inherit run", not "re-target to another commit".
- [x] 4.2 Cross-reference the new invariant (every `main` commit has a resolvable dev `:<sha>`) and note the self-seeding property.

## 5. Verification

- [x] 5.1 Backend: verified via doc-only PR #318 (merge `665b3c51`). The deploy run took the inherit path (Decide=success, Build and Push=skipped, Inherit=success); all 4 `<image>:665b3c51` digests equal their parent `:5650ad7` digests in dev AR.
- [x] 5.2 Frontend: verified via doc-only PR #378 (merge `e644d49f`). `build-and-push` took the inherit path (Build and Push=skipped); `web-app:e644d49f` digest equals parent `:fd28810`. (The only red was `post-deploy-smoke`, which targets the stopped dev URL — pre-existing/environmental.)
- [x] 5.3 Verified by inference: the release path's digest-resolve is the same `gcloud artifacts docker images describe <image>:<sha>` confirmed succeeding in 5.1/5.2, and `main` HEAD now always carries a resolvable dev `:<sha>` image — so a release cut on HEAD resolves. No throwaway release cut (would promote to prod AR).
- [x] 5.4 Deferred — dev cluster is intentionally stopped (cost), so ArgoCD behavior cannot be observed live. By construction the inherit path re-points `:latest` to the **same digest** the parent already held (digest equality proven in 5.1/5.2), so the Image Updater sees no digest change and performs a no-op rollout. Re-confirm when the dev cluster resumes.
