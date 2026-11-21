## 1. Evaluation harness (backend)

- [ ] 1.1 Re-capture the fixture of `ticket_sale_eval_integration_test.go` from current public pages (design D1): at least 4 artists and 10 sales that open after the capture time, including a lottery with a result date, a later round and a series with two or more upcoming sales, with `spEvalNow` set to the capture time; verify each expected sale against the page that announces it and record the artists, series and capture time in the harness doc comment
- [ ] 1.2 Record per call the search queries, tokens, cost at the 2027-01-01 price (`Pricing2027`), latency and empty or failed responses, and write the results under `testdata/ab_results/` (design D2); verify with a one-case run (`GEMINI_SP_EVAL=1 GEMINI_SP_EVAL_CASES=<case> GEMINI_SP_EVAL_REPS=1`, dev ESC `pulumiConfig.geminiSearchApiKey`) that the file has every column

## 2. Evaluation runs (backend)

- [ ] 2.1 Run `gemini-3.8-flash` and `gemini-4-hydrogen`, thinking `low`, 3 repetitions on every fixture case, within a day of the capture; verify the result files are committed and the per-sale comparison and the D3 verdict are recorded in `docs/gemini-concert-searcher-tuning.md`
- [ ] 2.2 Only if 2.1 fails D3 on missed sales: evaluate `gemini-4-hydrogen` with the completion line added to `systemInstructionPublishedSales` (design D4), same runs; verify the D3 verdict is recorded, and that the searcher stays on `gemini-3.8-flash` with the reason recorded when neither instruction passes

## 3. Adopt (backend)

- [ ] 3.1 If `gemini-4-hydrogen` passed, set `defaultPublishedSaleSearchModel` to it and adopt the instruction that passed (design D5); verify the config unit test asserts the new default and the searcher's request test asserts the instruction
- [ ] 3.2 Open the backend PR, merge it after CI and review, and cut a release; verify the release tag exists and the automated prod-pin bump moved the `sales-phase-discovery` image to it

## 4. Configuration (cloud-provisioning)

- [ ] 4.1 If 3.1 changed the model, set `GCP_GEMINI_SEARCH_MODEL_EXTRACT` in `k8s/namespaces/backend/base/cronjob/sales-phase-discovery/configmap.env` (and its comment) to the adopted model, merged after the 3.2 release (design D5); verify `kustomize build k8s/namespaces/backend/overlays/prod` renders the adopted model for `sales-phase-discovery-job-config` and the concert-discovery values unchanged, and after the ArgoCD sync that the prod ConfigMap carries it
