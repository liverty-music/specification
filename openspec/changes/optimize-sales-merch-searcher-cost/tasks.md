## 1. Backend — merch defaults

- [x] 1.1 In `pkg/config`, change `defaultMerchModel` from `gemini-3.1-flash-lite` to `gemini-3.6-flash` and `defaultMerchThinkingLevel` from `high` to `medium`; update the merch model/thinking comments accordingly.
- [x] 1.2 Add/adjust config unit tests asserting `MerchModel()` defaults to `gemini-3.6-flash` and `MerchThinking()` defaults to `medium`.

## 2. Backend — test fixtures (already drafted locally)

- [x] 2.1 Commit the refreshed `sales_phase_searcher_integration_test.go` fixture: series `Vaundy JAPAN ARENA TOUR 2027-2028`, ground truth = `ぴあ抽選先行` (apply_start 2026-07-16 12:00 JST), thinking loop = `{medium}`, `SALES_PHASE_TEST_MODEL_EXTRACT` override retained.
- [x] 2.2 Commit the refreshed `merch_searcher_integration_test.go` Vaundy case series (`Vaundy JAPAN ARENA TOUR 2027-2028`).
- [x] 2.3 Run `make check` (lint + unit tests) green.

## 3. A/B validation (done — record here)

- [x] 3.1 Local A/B (dev key, thinking=medium): sales-phase flash-lite 0 phases vs 3.6-flash 1/1 exact (`ぴあ抽選先行`, post-cutoff, apply/result/payment + pia URL correct).
- [x] 3.2 Local A/B: merch flash-lite hallucinated `.../category_id=3428` vs 3.6-flash correct `store.plusmember.jp/yorushika/`.
- [x] 3.3 Decision: migrate both sales-phase and merch extract to `gemini-3.6-flash` + thinking `medium`. Fan-out cost drop verified post-deploy (metadata invisible).

## 4. Prod rollout

- [ ] 4.1 Cut a backend release (next minor) including the merch defaults + fixtures. merch-discovery inherits the new defaults; verify a dev AR image exists before release.
- [ ] 4.2 In cloud-provisioning `sales-phase-discovery` configmap.env: set `GCP_GEMINI_SEARCH_MODEL_EXTRACT=gemini-3.6-flash` and `GCP_GEMINI_SEARCH_THINKING_EXTRACT=medium`; keep `GCP_GEMINI_SEARCH_MODEL_PARSE=gemini-3.1-flash-lite`. Bump the sales-phase-discovery job pin (auto pin-bump may omit it — verify/bump manually).
- [ ] 4.3 Confirm merch-discovery prod job picks up the new backend image (its pin bumps with the release); it has no env override so it inherits `gemini-3.6-flash` / `medium`.

## 5. Verification & close-out

- [ ] 5.1 Confirm ArgoCD syncs; sales-phase-discovery and merch-discovery jobs run the new model (`model_grounded`/`model=gemini-3.6-flash` in logs).
- [ ] 5.2 Verify in the billing export that the "search query gemini 3 paid" SKU drops for the sales/merch run hours after rollout.
- [ ] 5.3 Spot-check discovery quality: sales-phase surfaces current/post-cutoff sale phases; merch resolves correct official URLs (no fabricated deep links).
- [ ] 5.4 Verify the change (`/opsx:verify`) and archive it once all tasks are complete and shipped.
