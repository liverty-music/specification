## 1. Tour detail page links (components/entity/concert/search, backend)

- [ ] 1.1 After `officialPageLinks`, fetch the first 3 concert-tier links with the guarded client in parallel and collect their same-domain links that are neither the top page nor a top-page link, de-duplicated and in page order, capped at 20 pages in total (design D1); verify `httptest` unit tests annotated with the spec scenarios "Tour detail pages behind a live page", "Only the first 3 concert pages followed", "News page not followed", "Concert page link to another domain ignored", "At most 20 pages" and "Concert page unavailable", and that the existing scenario tests of the requirement still pass
- [ ] 1.2 Append the detail links to the prompt's linked-pages block and to `LinkedPageURLs` (design D2); verify a request-capture unit test shows top-page links first, then the detail links, and the prompt unchanged when no concert page yields links
- [ ] 1.3 Update `docs/gemini-concert-searcher-tuning.md` (pipeline section) and the package `AGENTS.md` to describe the second fetch level and the 20-page cap; verify both name the 3-page and 20-page limits

## 2. Evaluation harness (backend)

- [ ] 2.1 Re-capture `testdata/ab_ground_truth.json` from the official pages of the 4 current artists and add at least 3 artists whose prod searches used more than 30 queries (public official pages only), with `evaluation_from` set to the capture date; verify `LoadGroundTruth` parses it and the harness README lists the artists and capture dates
- [ ] 2.2 Add harness switches for detail links on/off, model, thinking level, the search-cap prompt line and Google Search on/off (design D3), recording per call recall, search queries, tokens, cost at the 2027-01-01 price, latency, empty responses and `groundingChunks` presence; verify a smoke run (`GEMINI_AB_EVAL_SMOKE=1`, dev ESC `pulumiConfig.geminiSearchApiKey`) writes all these columns for one cell

## 3. Evaluation runs (backend)

- [ ] 3.1 Run 1 (baseline vs detail links on `gemini-3.8-flash`, 3 reps, all fixture artists); verify the result files are committed under `testdata/ab_results/` and the tuning doc records the D4 verdict
- [ ] 3.2 Run 2 (the run-1 winner on `gemini-4-hydrogen`, thinking `low`); verify the tuning doc records the D4 verdict including p90 latency and the `groundingChunks` result, and add that result to backend #772
- [ ] 3.3 Run 3 on the winning model (search cap; lowest thinking level; Google Search off for artists with detail links); verify the tuning doc records a D4 verdict per variant, and, if Google Search off meets D4, an issue for the follow-up change exists

## 4. Adopt the evaluated settings (backend)

- [ ] 4.1 Apply the adopted model and thinking level to `defaultConcertSearchModel` / `defaultConcertSearchThinking` and the search cap to `systemInstruction`, or record in the tuning doc that the current values stay (design D5); verify the config unit tests assert the adopted defaults
- [ ] 4.2 Open the backend PR, merge it after CI and review, and cut a release; verify the release tag exists and the automated prod-pin bump moved the concert-discovery image to it

## 5. Configuration (cloud-provisioning)

- [ ] 5.1 Remove the stale `GCP_GEMINI_SEARCH_MODEL_EXTRACT=gemini-3.6-flash` / `GCP_GEMINI_SEARCH_THINKING_EXTRACT=medium` lines and their two-step comment from the base `cronjob/concert-discovery/configmap.env` (design D5); verify `kustomize build k8s/namespaces/backend/overlays/prod` still renders `gemini-3.8-flash` / `low` for the job, and the dev overlay renders the code defaults
- [ ] 5.2 If 4.1 changed the model or thinking level, set the same values in the prod overlay's `cronjob/concert-discovery/configmap.env` and its comment, in the same release window as 4.2; verify the rendered prod ConfigMap matches the backend defaults

## 6. Production check

- [ ] 6.1 One week after the release runs in prod, compare `$ai_generation` (process `liverty-music-concert-discovery`) with 2026-10-21..11-20 (design D6); verify queries per call (mean, p90), the share of queries from calls over 20 queries, events per call and errors are recorded in the tuning doc, and that the projected monthly concert-discovery queries are below 4,000 or the gap is filed as an issue
