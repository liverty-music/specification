## 1. Admin area and venue normalization (components/entity/concert/search)

- [ ] 1.1 Make `geo.NormalizeAdminArea` pass ISO 3166-2 codes (any country) through upper-cased while still mapping Japanese prefecture names; verify `TestNormalizeAdminArea` covers scenarios "Prefecture in Japanese", "Prefecture in English", "Overseas venue" (TW-TPE) and "Unrecognized area" and passes
- [ ] 1.2 Move `NormalizeVenue` and its regexes out of `abeval_scoring.go` into its own gemini package file, keeping NFKC, middle-dot stripping and whitespace removal; verify `TestNormalizeVenue` (incl. the notation-variant cases) passes and the scenario "Same venue in two notations" holds through the repeat-removal path

## 2. Single grounded call with JSON output (components/entity/concert/search)

- [ ] 2.1 Make the single JSON slice the ConcertSearcher default: final system instruction and user prompt from design D3, full official-site URL, 2-month `TimeRangeFilter` truncated to seconds, `singleStepResponseSchema` with tours `minItems 1` and standalones exactly one event; verify a unit test asserts the request config (tools, schema, MIME type, no temperature, time range) for a built request
- [ ] 2.2 Remove the XML envelope parsing, the Step 2 parse call, `systemInstructionStep2Parse`, the multi-slice fan-out and the `ModelParse` requirement from the concert searcher; verify `go build ./...` and `go test ./internal/infrastructure/gcp/gemini/...` pass
- [ ] 2.3 Map the JSON response through the existing merge and verify unit tests for the scenarios "Past event left out", "Two standalone shows with one title", "First and second stage kept", "Identical event listed twice", "Former name kept", "Literal null start" pass against canned JSON responses
- [ ] 2.4 Verify the scope scenarios "Festival left out", "Cancelled show left out" and "Co-headliner bill organized by the artist" with one live run of `TestConcertSearcher_GroundingVariants` (variant FINAL) per fixture artist, recording recall and search queries per call

## 3. Empty responses and logging (components/entity/concert/search)

- [ ] 3.1 Return a permanent `errNoCandidates` when a response has no candidates, without retrying, and log usage and prompt feedback; verify unit tests for "Response without a candidate" (one attempt, error), "Recovered on retry" and "All attempts transient" pass
- [ ] 3.2 Verify a SearchNewConcerts unit test with the searcher mocked to return the new error marks the SearchLog failed (existing scenario "External search fails")
- [ ] 3.3 Enable `include_server_side_tool_invocations` on the grounded call and log `search_queries` (list) and `web_search_queries` (count) in the response log, falling back from groundingMetadata to the tool-call parts; verify a unit test feeds a response with Google Search tool-call parts and asserts the logged queries

## 4. Configuration and wiring

- [ ] 4.1 Set code defaults for the concert searcher to `gemini-3.8-flash` and thinking `low`, and set `OmitTemperature` in the job, consumer and server DI; verify `pkg/config` tests and `go build ./...` pass and sales-phase wiring is unchanged
- [ ] 4.2 Add `gemini-3.8-flash` to the A/B pricing table if missing and update the harness README for the new default; verify the harness compiles with `go vet -tags=integration ./internal/infrastructure/gcp/gemini/`
- [ ] 4.3 Open the backend PR (rebased from `test/refresh-vaundy-ab-fixture`), get CI green including `make lint`, merge and cut a release; verify the release tag exists

## 5. Rollout (cloud-provisioning)

- [ ] 5.1 Update the prod `concert-discovery` ConfigMap: `GCP_GEMINI_SEARCH_MODEL_EXTRACT=gemini-3.8-flash`, `GCP_GEMINI_SEARCH_THINKING_EXTRACT=low`, `GCP_GEMINI_SEARCH_CACHE_TTL=96h` (branch `chore/extend-concert-search-cache-ttl`); verify `kubectl kustomize` renders the three values
- [ ] 5.2 Narrow the prod suspend patch target to `sales-phase-discovery-app` (dev keeps both); verify `kubectl kustomize` shows `suspend: true` only on sales-phase-discovery in prod
- [ ] 5.3 Bump the prod image pin to the new backend release and merge the cloud-provisioning PR; verify ArgoCD is Synced on the merge commit and `concert-discovery-app` is not suspended
- [ ] 5.4 After the first scheduled run, verify in Cloud Logging that responses carry `search_queries`, the job reports its failures truthfully, and the billing export's search-query count for that hour matches the logged distinct queries
