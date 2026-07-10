## 1. JS beam-tracking optimization (frontend)

- [ ] 1.1 In `concert-highway.ts`, add a cached anchor→element map (`Map<number, HTMLElement>` keyed by beam-anchor index); populate it in `buildBeamIndexMap()` by querying `[data-beam-index]` once per rebuild, and clear/rebuild it on `dateGroupsChanged` and `detaching`.
- [ ] 1.2 Rewrite `updateBeamPositions()` to read from the cached map instead of a per-frame `querySelector`, preserving the existing missing-element skip.
- [ ] 1.3 Split `updateBeamPositions()` into a read phase (collect all `getBoundingClientRect` results into a local array) followed by a write phase (apply all `--beam-h` / `--beam-top-pct` writes) — no read/write interleave.
- [ ] 1.4 Confirm computed `--beam-h` / `--beam-top-pct` values are byte-identical to the previous implementation (same formulas, only reordered).

## 2. Dead-code cleanup (frontend)

- [ ] 2.1 Remove the unused `@keyframes beam-descend` from `event-card.css`; grep the repo to confirm no `animation:` reference remains.

## 3. Tests & local verification

- [ ] 3.1 Update/extend `concert-highway.spec.ts` to assert the cached anchor→element map is built on `dateGroups` change and that `updateBeamPositions` resolves cards from it (no per-frame query); keep the existing detach/cancel assertions.
- [ ] 3.2 `make check` (lint + unit) passes; run the existing dashboard/welcome E2E projects to confirm no regression.
- [ ] 3.3 Manual scroll check on the Welcome preview (beam-dense) confirming visually identical beam behavior.

## 4. Ship to prod

- [ ] 4.1 Open the frontend PR, drive CI green (Test/Smoke/E2E/Lint/Visual), address any review, and merge.
- [ ] 4.2 Cut the frontend Release (next patch after v1.24.0) from the merge commit; confirm the automated prod pin-bump lands and ArgoCD reports Synced/Healthy on the new tag.
- [ ] 4.3 Verify prod is healthy (web-app pod on the new tag, HTTP 200) and beams render on the live dashboard/Welcome preview.

## 5. Archive

- [ ] 5.1 After prod verification, run `openspec archive optimize-concert-highway-beam-tracking` (via verify-before-archive) to fold the `concert-highway-ce` delta into the main spec.
