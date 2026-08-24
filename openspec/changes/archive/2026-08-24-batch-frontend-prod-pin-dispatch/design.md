## Context

The prod pin-bump automation (`automate-prod-pin-bump`, #553) was designed around **one dispatch per release component**: `component: "backend"` covers four backend images, `component: "frontend"` covers the (then single) `fan-web` bundle. `bump-prod-pin.yml` maps a component to its image set and pins them in one commit; a `concurrency: { group: bump-prod-pin, cancel-in-progress: false }` serializes bumps, and a fetch-rebase-retry push loop absorbs the backend-vs-frontend interleave (disjoint overlay files).

When the admin and organizer console bundles were added, `push-image.yaml` was extended to emit **three** dispatches with three *new* component values (`frontend`, `frontend-admin`, `frontend-organizer`) — rather than expanding the existing `frontend` component's image set the way `backend` already handles four images. All three frontend pins live in one file (`k8s/namespaces/frontend/overlays/prod/kustomization.yaml`), so the three dispatches are three near-simultaneous writers to the same file, all in the one `bump-prod-pin` concurrency group.

Authoritative GitHub Actions behavior: a concurrency group's default is `queue: single` — "at most one job or workflow run can be pending; when a new run queues, any existing pending run in the same group is canceled and replaced." `cancel-in-progress: false` protects the *running* run only, not a superseded *pending* one. With three dispatches → one running + one pending, the third evicts the second. One frontend bundle is silently never pinned. Reproduced on v1.58.0 and v1.58.1.

## Goals / Non-Goals

**Goals:**
- Eliminate the silent per-release bundle drop at its structural root (the fan-out), not just mask it.
- Restore the spec's "one dispatch per release component" pattern: `frontend` covers all its bundles like `backend` covers its four images.
- Make a frontend release's bundles pin **atomically** — one commit, all-or-nothing.
- Keep the design the simplest form that is correct; add no machinery that guards races the root fix removes.

**Non-Goals:**
- Adopting ArgoCD Image Updater for prod (deliberately rejected: prod pins to immutable semver tags with release-driven provenance and no-downgrade — `enable-prod-ar-immutable-tags` #274). It stays prod-disabled.
- Changing the git-push-from-dispatch model (chosen over clone-and-push for auth blast-radius reasons — D1 of #553), the provenance gate, the no-downgrade guard, or the admin-gated `workflow_dispatch` recovery path.
- Any proto/BSR/runtime-code change.

## Decisions

### D1: Collapse the frontend fan-out into one `component: "frontend"` dispatch

`push-image.yaml`'s `dispatch-prod-pin` job already `needs: [build-and-push, build-and-push-admin, build-and-push-organizer]` — it blocks on all three builds before emitting anything, so splitting into three dispatches buys **no** timing benefit. Emit one `component: "frontend"` dispatch and let `bump-prod-pin.yml` expand it to all three frontend bundle images (exactly as `component: "backend"` expands to four). This removes the third queued run, so the pending-eviction race cannot occur; it also cuts CI 3→1 (one federate / checkout / provenance loop / kustomize build / push) and makes the pin atomic (one commit).

**Alternatives considered:**
- **`queue: max`** (allow up to 100 pending, FIFO — GitHub, 2026-05-07). A one-line fix that stops the eviction but keeps three runs, three commits, a transient mixed-version window, and three writers to one file. Masks the fan-out instead of removing it. Rejected as the primary fix (see D3).
- **Per-component concurrency groups.** Lets the three run in parallel — more same-file push contention, more rebase-retry churn, still non-atomic. Strictly worse than one run.

### D2: All-or-nothing, mirroring the backend partial-retag rule

The single frontend dispatch is emitted only when **all three** bundle retags succeed; if any fails, no dispatch (no bundle is pinned). This mirrors the existing backend rule ("a partially-failed retag SHALL NOT dispatch") and is simpler than carrying a dynamic "which bundles succeeded" list. All three bundles come from the same release commit, so a build failure means the release is incomplete and should not be partially pinned — fail loudly, recover via the admin path.

**Alternative:** dynamic partial-success (pin the bundles that built). Rejected: adds payload/edit complexity to salvage a rare case that all-or-nothing handles more safely (an incomplete release should not go partially live).

### D3: Add no concurrency insurance (no `queue: max`, no reconcile job)

Once the fan-out is gone, the only concurrent writers to the `bump-prod-pin` group are a backend release and a frontend release — two writers, touching **disjoint** overlay files. That is precisely the one-running-plus-one-pending case the existing `concurrency` + rebase-retry already handle correctly (eviction needs a *third* queued run). So `queue: max`, per-component groups, and a post-release reconcile job would all guard a three-writer race that no longer exists — added surface for no live benefit. The simplest correct design leaves the concurrency block unchanged. (If a *third* independently-releasing writer to this group is ever introduced, revisit `queue: max` then — cheap, one line.)

### D4: Consume-side mapping + transitional back-compat

`bump-prod-pin.yml` maps `component: "frontend"` to the three frontend image entries + the `app.kubernetes.io/version` label (fan-web as the primary label source, unchanged) + the single frontend overlay path, editing and committing them in one pass. The old `frontend-admin` / `frontend-organizer` component branches MAY be retained for one release cycle so an in-flight old-style dispatch is not orphaned, then removed once no release emits them.

## Risks / Trade-offs

- **A slow/failed single bundle now blocks the whole frontend pin (all-or-nothing).** Accepted: the three bundles ship from one release; a partial release should not go live. The admin `workflow_dispatch` recovery path remains for exceptional manual pinning.
- **Transitional window.** Until the frontend workflow change ships, an old three-dispatch release still races. Mitigation: land the emit-side (frontend) and consume-side (cloud-provisioning) changes together, and keep the old component branches for one cycle (D4) so a straddling dispatch still applies.
- **Spec was itself drifted** (it still described `frontend` as the single `fan-web` entry, never updated for admin/organizer). This change reconciles the spec to the multi-bundle reality in the *aligned* one-dispatch form, so spec and implementation converge rather than both carrying the fan-out.
- **Loss of independent per-bundle pinning cadence.** Trivial in practice: all three are always cut from the same frontend release at the same tag, so there is no real independent cadence to lose.
