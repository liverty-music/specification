## 1. Consume side — `cloud-provisioning/.github/workflows/bump-prod-pin.yml`

- [x] 1.1 Extend the `frontend` component mapping to cover all three prod bundle images (`fan-web`, `admin-console-web`, `organizer-console-web`): the provenance `crane manifest` loop, the `yq` `newTag` + inline `# commit <sha>` trailer rewrite, and the overlay path SHALL all iterate the three frontend images (mirroring how `backend` iterates its four) (D1, D4)
- [x] 1.2 Keep the `app.kubernetes.io/version` label bump sourced from the primary bundle (`fan-web`) only — unchanged behavior (D4)
- [x] 1.3 Ensure all three frontend `newTag` rewrites happen in one edit pass and land in a single commit + single `kustomize build` + single push (atomic) (D1, spec: single-commit)
- [x] 1.4 Retain the `frontend-admin` / `frontend-organizer` component branches as a transitional single-image alias for one release cycle so an in-flight old-style dispatch is not orphaned; mark them for removal (D4)
- [x] 1.5 Correct the stale `concurrency` comment ("a queued bump waits for the running one rather than being dropped") — document `queue: single` semantics and that, post-fan-out-removal, the only concurrent writers are backend vs frontend (disjoint files), so no `queue: max` is needed (D3)
- [x] 1.6 Leave the `concurrency` block, provenance gate, no-downgrade guard, and admin-gated `workflow_dispatch` recovery path unchanged (Non-Goals)

## 2. Emit side — `frontend/.github/workflows/push-image.yaml`

- [x] 2.1 Collapse the three `dispatch-prod-pin` steps (`frontend`, `frontend-admin`, `frontend-organizer`) into a **single** `component: "frontend"` `repository_dispatch` (D1)
- [x] 2.2 Gate the single dispatch on **all three** bundle retags succeeding — dropped `always()` so the default `needs: [build-and-push, build-and-push-admin, build-and-push-organizer]` success gate skips the job (hence the dispatch) if any bundle retag fails — all-or-nothing (D2, spec: partial-failed frontend)
- [x] 2.3 Confirm no other consumer of the removed `frontend-admin` / `frontend-organizer` dispatch component values exists (only `bump-prod-pin.yml`'s retained transitional aliases + descriptive comments + the operator runbook remain; no workflow still *emits* those component values)

## 3. Verification

- [x] 3.1 Dry-run / trace the frontend release path to confirm exactly one `bump-prod-pin` dispatch is emitted with `component: "frontend"` — static: the job now has a single dispatch step emitting only `component:"frontend"` (grep-confirmed)
- [x] 3.2 On the next real frontend release: confirm `bump-prod-pin` runs exactly once for frontend (no `cancelled` sibling run), and the prod overlay's `fan-web` + `admin-console-web` + `organizer-console-web` `newTag` all move to the release tag in a **single commit** — VALIDATED on **v1.59.0**: one `component=frontend` dispatch run (`completed/success`, no cancelled sibling; a coinciding `component=backend` v1.59.0 dispatch also succeeded — the 2-disjoint-writer case), and cloud-provisioning commit `baafd5f81e` "pin frontend prod overlay to v1.59.0" moved all three `newTag`s in ONE commit (contrast v1.58.3's separate per-component commits + a cancelled run)
- [x] 3.3 Confirm ArgoCD auto-syncs all three frontend deployments to the release tag without a manual recovery bump (the defect this change removes, reproduced on v1.58.0 / v1.58.1) — VALIDATED on v1.59.0: `fan-web-app` / `admin-console-web-app` / `organizer-console-web-app` all at `v1.59.0`, READY 1 / AVAIL 1, no manual recovery needed
- [x] 3.4 Negative check: verify a single-bundle build failure results in **no** dispatch (all-or-nothing) — static: `needs: [all three]` with no `always()` skips the whole `dispatch-prod-pin` job if any bundle retag fails

## 4. Ship

- [x] 4.1 Open the cloud-provisioning PR (Conventional Commits, mandatory body + `Refs: #<issue>`); CI green — PR #448 (bump-prod-pin.yml + runbook), merged (4adaf66); Refs specification#852
- [x] 4.2 Open the frontend workflow PR (Conventional Commits, mandatory body + `Refs: #<issue>`); CI green — PR #568 (push-image.yaml), merged (ebc72be); Refs specification#852
- [x] 4.3 Land both together (consume side first) so no release straddles a half-applied change — merged #448 (consume) then #568 (emit); transitional aliases (1.4) cover a straddling dispatch
- [x] 4.4 After a subsequent frontend release validates 3.2–3.3, remove the transitional `frontend-admin` / `frontend-organizer` aliases (follow-up) — v1.59.0 validated 3.2/3.3, so removed in cloud-provisioning PR #450: `bump-prod-pin.yml` `component` choice + payload validation now accept only `backend | frontend`, the two transitional case branches dropped, runbook + prod-overlay comments updated
