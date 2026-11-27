## 1. backend: Flex in Concert.Search (components/entity/concert/search)

- [ ] 1.1 Add `ServiceTier` to `gemini.Config` and `GCP_GEMINI_CONCERT_SEARCH_SERVICE_TIER` to `pkg/config` (default `flex`, `standard` sends no tier), set it on every concert search call, and make the call timeout 15 minutes at the flex tier and 120 s otherwise (design D3); verify with searcher unit tests for the scenarios "Late answer", "Busy on every attempt" and "No answer within 15 minutes" (fake clock or injected timeout), and a config test for the default and both values
- [ ] 1.2 Report the service tier on each LLM generation as `service_tier` (design D7) and verify with the generation reporter test for the scenario "Lower-priced service level"; also read how the searcher classifies a 403 spend-cap refusal and record the answer in design.md Risks (design.md, the spend-cap risk)

## 2. backend: background search (components/usecase/concert/search-new-concerts)

- [ ] 2.1 Add the `search-concerts` workflow `ConcertUseCase.RunSearch`, one attempt per run with the steps of design D2. Move the body of `executeSearch` into it, and make `search` return busy or failed as values so the step retry policy never runs.

  Verify with usecase unit tests (Flow and operations mocked) for these scenarios:
  - "The search runs in the background": "Service busy for 3 hours" (the next attempt started with a 1, 2, 4 … minute delay capped at 60, then completed) and "Queued until late" (failed, and no signal on attempt 1);
  - "Each attempt checks again before searching": "Represented while waiting" and "Search replaced";
  - "The search is recorded": "Productive search", "Nothing new", "External search fails" and "Service busy for a whole day";
  - "New concerts are handed on once per search": "Two series found", "Nothing new" and "Cannot be started";
  - "Each search reports its outcome": "Nothing new", "Search failed", "Failure without a kind" and "Busy for a whole day".
- [ ] 2.2 Make SearchNewConcerts start the first attempt after the pending upsert (id `search-concerts:<artist>:<search time µs>:1`, queue `concert-search`, no deadline). It returns only an error, the previews are deleted, and `pendingTimeout` rises to 20 h (design D1, D5, D6).

  Verify with usecase unit tests for these scenarios:
  - "The search runs in the background": "Daily run starts searches and ends" and "Cannot be started";
  - "Artist data required": "Artist without MBID" (the check runs in SearchNewConcerts before the upsert, which fails with Internal, leaves the ConcertSearch unchanged and starts no attempt; design D1);
  - "Skip when recently searched or discovered": "Searched 2 hours ago", "New concert found 3 days ago", "Another search running", "Abandoned search" and "Previous search failed".
- [ ] 2.3 Register `search-concerts` and the `concert-search` queue (concurrency 8) in the workflow worker, and build the concert searcher there (design D1, D4).

  Verify with the workflow runtime integration test against Postgres for these scenarios of "The search runs in the background":
  - "Same attempt started twice";
  - "Eight at once";
  - "Waiting retries hold no place": 8 delayed attempts and a ninth that runs at once.
- [ ] 2.4 Update the daily job and the first-follow consumer for the error-only SearchNewConcerts and keep their tests passing; release backend once the image built from the merge exists, and record the version for task 3.2

## 3. cloud-provisioning: pins and rollout

- [ ] 3.1 Move `GCP_GEMINI_SEARCH_MODEL_EXTRACT` and `GCP_GEMINI_SEARCH_THINKING_EXTRACT` from the prod `concert-discovery` ConfigMap to the prod `fan-api` ConfigMap the worker reads, add `GCP_GEMINI_CONCERT_SEARCH_SERVICE_TIER=flex` beside them, keep `GCP_GEMINI_SEARCH_CACHE_TTL` in the job (design D8), and verify with `kustomize build` of the prod overlay that the worker's ConfigMap carries the three values and the job's carries the cache TTL only
- [ ] 3.2 Bump the prod release pins of the backend images to the release of task 2.4 in the same PR and merge (ArgoCD syncs it to prod); say so in the report

## 4. Production check and observation (read-only)

- [ ] 4.1 After the first 18:00 JST run following the rollout, confirm in prod that the job finished within 5 minutes, that each Artist due for a search has a `search-concerts` workflow, that `$ai_generation` events carry `service_tier = flex`, and that at least one search reached completed or failed
- [ ] 4.2 After 3 days, collect the observation of design.md (success and 503/429 counts, latency, attempts per search, time from search time to end, searches that gave up at 20 hours) and write it with a recommendation on the standard-tier fallback and the freshness window into design.md Results
- [ ] 4.3 Update the held change `measure-official-page-change-detection` (its plan worktree) to the new structure: its D1 (where the check runs), D5 and D6 (searches now end hours after 18:00 JST and the outcome comes from `record-end`), then resume it with plan-change step 4
