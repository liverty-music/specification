## 1. backend: Flex in Concert.Search (components/entity/concert/search)

- [ ] 1.1 Add `ServiceTier` to `gemini.Config` and `GCP_GEMINI_CONCERT_SEARCH_SERVICE_TIER` to `pkg/config` (default `flex`, `standard` sends no tier), set it on every concert search call, and make the call timeout 15 minutes at the flex tier and 120 s otherwise (design D3); verify with searcher unit tests for the scenarios "Late answer", "Busy on every attempt" and "No answer within 15 minutes" (fake clock or injected timeout), and a config test for the default and both values
- [ ] 1.2 Report the service tier on each LLM generation as `service_tier` (design D7) and verify with the generation reporter test for the scenario "Lower-priced service level"; also read how the searcher classifies a 403 spend-cap refusal and record the answer in design.md Risks (design.md, the spend-cap risk)

## 2. backend: background search (components/usecase/concert/search-new-concerts)

- [ ] 2.1 Add the `search-concerts` workflow `ConcertUseCase.RunSearch` with the steps of design D2, moving the body of `executeSearch` into it, and verify with usecase unit tests (Flow and operations mocked) for the scenarios "Productive search", "Nothing new" (both requirements), "External search fails", "Two series found" and "Cannot be started" of "New concerts are handed on once per search"
- [ ] 2.2 Make SearchNewConcerts start `search-concerts` (id `search-concerts:<artist>:<search time µs>`, queue `concert-search`, deadline search time + 20 h) after the pending upsert, return only an error, delete the previews, and raise `pendingTimeout` to 20 h (design D1, D5, D6); verify with usecase unit tests for "Daily run starts searches and ends", "Cannot be started" of "The search runs in the background", and "Searched 2 hours ago", "New concert found 3 days ago", "Another search running", "Abandoned search" and "Previous search failed"
- [ ] 2.3 Register `search-concerts` and the `concert-search` queue (concurrency 8) in the workflow worker and build the concert searcher there (design D1, D4), and verify with the workflow runtime integration test against Postgres for "Same search started twice", "Eight at once", "Service busy for 3 hours" (a step failing with Unavailable then succeeding) and "Service busy for a whole day" (a short deadline in the test)
- [ ] 2.4 Update the daily job and the first-follow consumer for the error-only SearchNewConcerts and keep their tests passing; release backend once the image built from the merge exists, and record the version for task 3.2

## 3. cloud-provisioning: pins and rollout

- [ ] 3.1 Move `GCP_GEMINI_SEARCH_MODEL_EXTRACT` and `GCP_GEMINI_SEARCH_THINKING_EXTRACT` from the prod `concert-discovery` ConfigMap to the prod `fan-api` ConfigMap the worker reads, add `GCP_GEMINI_CONCERT_SEARCH_SERVICE_TIER=flex` beside them, keep `GCP_GEMINI_SEARCH_CACHE_TTL` in the job (design D8), and verify with `kustomize build` of the prod overlay that the worker's ConfigMap carries the three values and the job's carries the cache TTL only
- [ ] 3.2 Bump the prod release pins of the backend images to the release of task 2.4 in the same PR and merge (ArgoCD syncs it to prod); say so in the report

## 4. Production check and observation (read-only)

- [ ] 4.1 After the first 18:00 JST run following the rollout, confirm in prod that the job finished within 5 minutes, that each Artist due for a search has a `search-concerts` workflow, that `$ai_generation` events carry `service_tier = flex`, and that at least one search reached completed or failed
- [ ] 4.2 After 3 days, collect the observation of design.md (success and 503/429 counts, latency, run time to end, step attempts, runs stopped at the deadline) and write it with a recommendation on the standard-tier fallback and the freshness window into design.md Results
- [ ] 4.3 Update the held change `measure-official-page-change-detection` (its plan worktree) to the new structure: its D1 (where the check runs), D5 and D6 (searches now end hours after 18:00 JST and the outcome comes from `record-end`), then resume it with plan-change step 4
