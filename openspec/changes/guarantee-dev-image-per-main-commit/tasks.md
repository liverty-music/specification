## 1. Specification (this change)

- [ ] 1.1 Open PR in `specification` with the `prod-image-pipeline` delta (proposal/design/specs/tasks); pass `buf-pr-checks.yml` and review. No proto change → no BSR/Release needed.
- [ ] 1.2 After all implementation PRs (sections 2–4) merge and verify (section 5), run the openspec sync + archive for this change.

## 2. Backend pipeline (`backend/.github/workflows/deploy.yml`)

- [x] 2.1 Remove `paths:` from the `push` trigger so every push to `main` starts the workflow (keep `release: [published]`).
- [x] 2.2 Add a build-vs-inherit decision step: compute changed files over `${{ github.event.before }}..${{ github.sha }}` and match against the build glob set (`**.go`, `go.mod`, `go.sum`, `Dockerfile`, `.github/workflows/deploy.yml`); expose a boolean output (`build` vs `inherit`).
- [x] 2.3 Gate the existing build-and-push steps on the `build` decision (push-event only), preserving `:latest,:main,:<sha>` to dev AR for all 4 matrix images.
- [x] 2.4 Add the inherit path (push-event + `inherit` decision): per matrix image, resolve the dev-AR digest of `<image>:${{ github.event.before }}` and `crane copy` it to `<image>:${{ github.sha }}`, then re-point `:main` and `:latest`; no `docker build`.
- [x] 2.5 Add the parent-resolution fallback (zero `before` SHA / gap): try `:main` digest or `HEAD^1`'s `:<sha>`; if unresolvable, fail non-zero with an explicit "seed via a build-relevant file" message; never write `:<sha>` at a wrong digest.
- [x] 2.6 Update the release `Resolve dev AR digest` final error message and the `Verify release commit is on main` message: drop the "filtered-out / non-main commit" attribution and the "re-target to an earlier commit" / "main HEAD only" wording; state the invariant (a `main` HEAD always resolves; missing `:<sha>` means in-flight or a failed build/inherit). Keep the 6×60s retry.

## 3. Frontend pipeline (`frontend/.github/workflows/push-image.yaml`)

- [x] 3.1 Remove `paths:` from the `push` trigger (keep `release: [published]` and existing `workflow_dispatch`).
- [x] 3.2 Add the build-vs-inherit decision over `${{ github.event.before }}..${{ github.sha }}` against the frontend build glob set (`src/**`, `public/**`, `scripts/**`, `package.json`, `package-lock.json`, `vite.config.ts`, `Dockerfile`, `Caddyfile`, `.github/workflows/push-image.yaml`).
- [x] 3.3 Gate the existing build-and-push (incl. the `verify:build-templates` assertion) on the `build` decision.
- [x] 3.4 Add the inherit path for `web-app`: resolve `web-app:${{ github.event.before }}` digest and `crane copy` to `web-app:${{ github.sha }}`, re-point `:main`/`:latest`; no build; same fallback as 2.5.
- [x] 3.5 Update the release digest-resolve error message symmetrically with task 2.6.

## 4. Runbook (`cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md`)

- [x] 4.1 Revise the "Failure: dev AR `:<sha>` does not exist" section: remove the path-filter cause (now eliminated); state remaining causes are in-flight race or a failed build/inherit job; recovery is "re-run the build/inherit run", not "re-target to another commit".
- [x] 4.2 Cross-reference the new invariant (every `main` commit has a resolvable dev `:<sha>`) and note the self-seeding property.

## 5. Verification

- [ ] 5.1 Backend: after 2.x merges to `main` (self-seeds HEAD via the build path), push a doc-only commit to `main`; confirm the inherit path runs (no `docker build`), all 4 `<image>:<sha>` resolve in dev AR, and each equals its parent digest.
- [ ] 5.2 Frontend: same check with a doc-only commit; confirm `web-app:<sha>` resolves and equals parent digest.
- [ ] 5.3 Cut a throwaway pre-release (or dry-run via a test tag) on a doc-only `main` HEAD in one repo and confirm the release digest-resolve succeeds without the previous failure (clean up the test tag afterward).
- [ ] 5.4 Confirm dev ArgoCD did not roll back or thrash when `:latest` was re-pointed on an inherit push (no-op rollout at the same digest).
