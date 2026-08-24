## Why

A frontend release silently fails to pin one of its web bundles to prod on every cut. `push-image.yaml` emits **three** `repository_dispatch` events (`frontend`, `frontend-admin`, `frontend-organizer`) within one second, all landing in `bump-prod-pin.yml`'s single `concurrency` group. A concurrency group holds at most one running + one pending run (`queue: single`, the default); when the third dispatch queues it evicts the middle pending one, so one bundle is never pinned and stays on the previous release. This reproduced on both v1.58.0 and v1.58.1, each requiring a manual admin-gated recovery bump.

The three-way fan-out is drift, not design. The `prod-image-pipeline` spec already defines the pattern as **one dispatch per release component**: `component: "frontend"` (like `component: "backend"`, which covers four images in a single dispatch). When the admin and organizer console bundles were added, the implementation introduced two *new* component values and split into three dispatches — instead of expanding the existing `frontend` component's image set the way `backend` already does. That split is what created both the concurrency race and 3× the CI cost for what is logically one atomic operation: pin the frontend release's bundles.

## What Changes

- The frontend release path SHALL emit a **single** `component: "frontend"` `repository_dispatch` covering all frontend prod bundles (`fan-web`, `admin-console-web`, `organizer-console-web`), mirroring how `backend` covers its four images in one dispatch. **Remove** the `frontend-admin` and `frontend-organizer` component values and their separate dispatch steps.
- `bump-prod-pin.yml` SHALL map `component: "frontend"` to the full set of frontend prod images/labels and pin them in a **single commit** (one `kustomize build`, one push), the same multi-image handling it already applies to `component: "backend"`.
- Frontend pin-bumps become **atomic** (all bundles move together in one commit) and **all-or-nothing**: a partially-failed frontend retag SHALL NOT dispatch — mirroring the existing backend partial-retag rule — so prod never sees a half-pinned release or a transient mixed state.
- The `queue: single` concurrency behavior is **left unchanged**: once the fan-out is gone, the only concurrent writers are a backend release and a frontend release, which touch disjoint overlay files — exactly the one-running-plus-one-pending case the existing `concurrency` + fetch-rebase-retry already handle safely. No `queue: max`, no per-component groups, no reconcile job are added; they would guard a three-writer race that no longer exists.

## Capabilities

### Modified Capabilities
- `prod-image-pipeline`: the "Prod kustomize pin-bumps SHALL be automated via repository_dispatch" requirement changes so the frontend release emits one `component: "frontend"` dispatch covering all frontend bundles (removing the `frontend-admin`/`frontend-organizer` fan-out), and the bump pins them atomically in one commit with all-or-nothing partial-failure semantics.

## Impact

- **frontend** `.github/workflows/push-image.yaml`: `dispatch-prod-pin` job — collapse three dispatch steps into one `component: "frontend"` dispatch; keep the `needs: [build-and-push, build-and-push-admin, build-and-push-organizer]` gate but make it all-or-nothing (dispatch only if all three retags succeeded).
- **cloud-provisioning** `.github/workflows/bump-prod-pin.yml`: extend the `frontend` component's image/label/path mapping to cover `fan-web` + `admin-console-web` + `organizer-console-web` in a single edit pass; drop the `frontend-admin` / `frontend-organizer` component branches; correct the stale "a queued bump waits rather than being dropped" comment.
- No change to: the immutable-semver prod pinning model, the provenance gate (`crane manifest`), the no-downgrade guard, the admin-gated `workflow_dispatch` recovery path, ArgoCD auto-sync, or the dev-path `argocd-image-updater` (which stays prod-disabled). No proto/BSR/runtime-code change.
- Backwards compatibility: transitional — the bump workflow MAY retain the old `frontend-admin`/`frontend-organizer` component branches for one release cycle so an in-flight dispatch is not orphaned, then remove them.
