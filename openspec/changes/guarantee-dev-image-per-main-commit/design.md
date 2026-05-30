## Context

The prod release path (`prod-image-pipeline`) promotes a pre-built dev image to prod by resolving `dev-AR/<image>:<github.sha>` and `crane copy`-ing it — it never rebuilds. The dev `:<sha>` image is produced by the push-to-`main` path, which is gated by a GitHub Actions `paths:` filter (backend: `**.go`, `go.mod`, `go.sum`, `Dockerfile`, `deploy.yml`; frontend: `src/**`, `public/**`, `package.json`, … , `push-image.yaml`). A push whose changed files match none of these globs **does not trigger the workflow at all**, so that commit gets no dev `:<sha>` image.

Releases are cut on `main` HEAD. When HEAD is such a filtered-out commit, the release fails at digest-resolve after a ~5-minute retry budget. This bit the backend `v1.2.0` promotion (HEAD `efd340a` touched only `claude-code-review.yml`). The proposal chose the root-cause fix (option B): guarantee every `main` commit has a resolvable dev `:<sha>` image, rather than improve detection/messaging (option G) or add never-coming-vs-in-flight disambiguation (option A).

Constraints: must not rebuild on the inherit path (defeats the retag pattern's purpose and `ci-optimization` intent); must stay symmetric across backend (4-image matrix) and frontend (single `web-app`); must not require new IAM (existing dev-AR read/write credentials suffice); prod AR immutability and ArgoCD overlays are untouched.

## Goals / Non-Goals

**Goals:**
- Every commit that the push-to-`main` workflow observes as `github.sha` has a resolvable dev-AR `:<sha>` image — by build (relevant change) or by inheriting the parent's digest (no relevant change).
- Eliminate the "filtered-out commit" cause from the release digest-resolve failure set.
- Remove the self-contradictory "Cut releases on main HEAD only" guidance vs the runbook's re-target recovery.
- Keep backend and frontend pipelines symmetric.

**Non-Goals:**
- Giving *every intermediate commit* of a multi-commit push its own image. Only push tips (what `github.sha` resolves to, and what releases are cut on) are covered. Mid-push commits are not release targets.
- Changing the prod promotion (`crane copy` to prod AR), prod AR immutability, kustomize overlays, or ArgoCD.
- Reworking the dev ArgoCD Image Updater (`:latest`) flow.
- Adding Actions-API-based "is a build in flight?" detection (that was option A; B makes it unnecessary).

## Decisions

### D1. Replace the `paths:` *trigger gate* with an in-workflow build-vs-inherit decision

A `paths:`-filtered push never starts the workflow, so an "inherit on skip" job cannot run under the same trigger. **Decision:** drop `paths:` from the `push` trigger so every push to `main` starts the workflow, then branch internally:

```
push to main (always triggers)
   │
   ├─ compute changed files over the push range (event.before .. github.sha)
   │
   ├─ ANY match build globs?  ── yes ──► BUILD path (existing): docker build → push :latest,:main,:<sha>
   │
   └─ no ───────────────────────────────► INHERIT path (new): crane copy parent digest → :<sha> (+ :main,:latest)
```

The glob set that previously lived in `on.push.paths` moves into the decision step (e.g., a `dorny/paths-filter`-style step or an explicit `git diff --name-only "$BEFORE..$SHA"` against the glob list).

**Alternatives considered:**
- *Second workflow without a `paths:` filter, running only the inherit job* — rejected: both workflows would fire on a matching push and need mutual exclusion; doubles the surface.
- *Keep the filter, fix only messaging* (option G) — rejected by the proposal; leaves the invariant false.

**Trade-off:** every `main` push now spins a runner, including doc-only ones. The inherit path runs no Docker build (~10–15s of crane retag), so the added cost is runner startup, not build minutes — aligned with `ci-optimization` (avoid redundant *builds*).

### D2. Inherit from the prior `main` tip's digest (`github.event.before`)

The inherit path resolves the dev-AR digest of the **parent push tip** and copies it to the new `:<sha>`. **Decision:** use `github.event.before` as the parent SHA — it is the commit `main` pointed to before this push, and by induction it already has a dev `:<sha>` image.

```
crane copy dev-AR/<image>:<event.before>  ─(by digest)→  dev-AR/<image>:<github.sha>
```

This is byte-exact: a push that changed no build-relevant file yields bytes identical to the parent, so the parent's digest *is* this commit's image.

**Why `event.before` over `HEAD^1`:** a push that fast-forwards `main` by several commits has `github.sha` = tip and `event.before` = the pre-push tip; the range `before..sha` is exactly what the build-vs-inherit diff (D1) evaluates, so the same boundary defines both the decision and the inherit source. `HEAD^1` would be wrong for a multi-commit fast-forward.

**Changed-file diff uses the same `before..sha` range** so the build/inherit decision and the inherit source are consistent.

### D3. Inherit path writes the same tag set as build (`:<sha>`, `:main`, `:latest`)

`:<sha>` is mandatory (release resolve key). The inherit path also moves `:main` and `:latest` to the inherited digest so the dev ArgoCD Image Updater (which tracks `:latest`) sees a consistent pointer — re-pointing `:latest` at the parent digest is a no-op rollout (same image), which is the correct outcome for a no-build commit. Dev `:latest`/`:main` are mutable by design; `:<sha>` is unique so never conflicts.

### D4. Bootstrap is self-seeding; no manual seed step

The commit that *implements* this change edits `deploy.yml` / `push-image.yaml`, which are inside the build glob set — so that very push takes the BUILD path and produces a fresh `:<sha>` for HEAD. From then on the inductive chain holds (each new tip inherits or builds from a parent that already has an image). No manual digest seeding is required.

### D5. With the invariant true, the digest-resolve guard is simplified, not removed

The release path keeps the existing 6×60s (~5 min) retry, but its meaning narrows: the only legitimate missing-`:<sha>` causes become (a) genuine in-flight race — release cut seconds after a push, before the build/inherit job finished — and (b) a failed build/inherit job. "Filtered-out / never-coming" is gone, and "non-main commit" is already caught earlier by the ancestry guard. Error messages and the `Verify release commit is on main` guidance are updated to assert the now-true invariant (releasing on `main` HEAD is always valid).

## Risks / Trade-offs

- **Inductive-chain break: a silent inherit failure starves the next commit's parent.** → The inherit job fails loudly (non-zero exit) exactly like the build job; a gap is visible in CI and backfilled by re-running. Each `:<sha>` is independent, so a single backfill repairs the chain. `concurrency` (group = workflow+ref, `cancel-in-progress: false`) serializes main pushes, so a parent's image is settled before the child runs.
- **Force-push and branch-creation are not inheritable.** `github.event.before` is the zero SHA *only* on branch creation / ref deletion. On a **force-push** it is the previous, now-**orphaned** tip — a real non-zero SHA flagged by `github.event.forced == true` — which is not necessarily an ancestor of the new tip, so its bytes are not equivalent to the new commit's tree. Inheriting it would pin a wrong digest (the outcome the "missing parent" scenario forbids). → The decision step routes `github.event.created` (zero `before`) **and** `github.event.forced` to the **build** path; neither takes the inherit path. The inherit path's *transient* missing-parent case (a normal linear push whose parent `:<sha>` is briefly unresolvable) falls back only to the `:main` digest (the prior tip in linear history), **never** to `HEAD^1` (which on a multi-commit push is an intermediate commit, not a prior `main` tip). If even `:main` is unresolvable, fail loudly with a seed instruction.
- **Inductive-chain ordering (load-bearing `concurrency`).** `concurrency: { group: <workflow>-<ref>, cancel-in-progress: false }` serializes consecutive `main` pushes so push N+1's parent resolution observes push N's completed `:<sha>` write. Promoted to a SHALL in the spec and a task in §2/§3 (both workflows already carry the block; the change codifies it). Without it a merge train could break the chain.
- **Runner spin-up on every doc-only push.** → No Docker build on the inherit path; marginal cost is seconds. Acceptable per `ci-optimization` intent.
- **Multi-commit push where the tip looks doc-only but the range contains a real change.** → The decision diffs the whole `before..sha` range, not tip-vs-parent, so it BUILDs correctly. Mirrors GitHub's own collective paths-filter evaluation.
- **Divergence between the two pipelines over time.** → Spec requires symmetry; both deltas land in this change and the runbook documents one shared model.

## Migration Plan

1. Land the spec delta (this change) in `specification`, release + BSR n/a (no proto).
2. Implement `backend/deploy.yml` and `frontend/push-image.yaml` (these edits match the build globs → self-seed HEAD's image per D4). Verify each repo's next doc-only push to `main` produces a `:<sha>` via the inherit path.
3. Update `cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md`: the "dev AR `:<sha>` does not exist" mode no longer lists the paths-filter cause; recovery for a true race is "re-run the build/inherit run", and re-targeting is no longer needed for filtered commits.
4. **Rollback:** revert the workflow edits → pipeline returns to the prior `paths:`-gate behavior (safe; only re-introduces the original gap). No data or registry state to unwind.

## Open Questions

- Should the build-vs-inherit decision use a maintained action (`dorny/paths-filter`) or an inline `git diff --name-only "$BEFORE..$SHA"` against the glob list? Inline avoids an external dependency and keeps the glob list co-located with the inherit logic; the action is terser. (Lean inline.)
- Confirm dev-AR tag mutability policy permits re-pointing `:main`/`:latest` on the inherit path (expected yes — only prod AR carries `immutableTags: true`).
