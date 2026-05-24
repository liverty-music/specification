## 1. Verify the shipped grounded-extract architecture is on the worktree

Most of the work for this change has already landed on the `evaluate-gemini-search-model` worktree across commits `84f7399`..`bfbcf31`. These tasks confirm the shipped code matches the spec before any cleanup begins.

- [x] 1.1 Confirm `backend/internal/infrastructure/gcp/gemini/searcher.go` defines `runStep1Grounded` and `runStep2Parse` (and not `runStep1Search` / `runStep2Extract` / `runStep3Parse`).
- [x] 1.2 Confirm `defaultStep1Slices` lists exactly `tours_near`, `tours_far`, `standalones` with the from/to month offsets `(0,12)`, `(12,24)`, `(0,24)`.
- [x] 1.3 Confirm `assertStepInvariants` accepts step labels `"step1_grounded"` and `"step2_parse"` (and rejects everything else).
- [x] 1.4 Confirm `parseStep1Envelope`, `mergeAndDedupEnvelopes`, and `parseStep2Response` are implemented per the spec (no `<source url>` wrapping in merge; triple-key dedup in parseStep2Response).
- [x] 1.5 Confirm `EventDraft` carries `Title`, `SourceURL`, `Venue`, `Country`, `LocalDate`, `StartTime`, `OpenTime`.
- [x] 1.6 Confirm `SearchMetadata` carries `Step1Grounded` and `Step2Parse` (and not the `Step1Search` / `Step2Extract` / `Step3Parse` fields from the abandoned three-step proposal).
- [x] 1.7 Confirm both Step 1 system instructions are in Japanese and follow the five-step numbered workflow.
- [x] 1.8 Confirm both prompt templates accept four positional `%s` placeholders (`from_date`, `to_date`, artist, host).

## 2. Remove dead `ModelDiscovery` configuration plumbing

The shipped code never calls `Config.modelDiscovery()` or `GCPConfig.SearchModelDiscovery()`. The spec for `gemini-searcher-config` defines only `ModelExtract` and `ModelParse`. Remove the dead path.

- [x] 2.1 In `backend/pkg/config/config.go`, delete the `GeminiSearchModelDiscovery` field on `GCPConfig`.
- [x] 2.2 In `backend/pkg/config/config.go`, delete the `defaultSearchModelDiscovery` constant.
- [x] 2.3 In `backend/pkg/config/config.go`, delete the `SearchModelDiscovery()` helper.
- [x] 2.4 In `backend/internal/infrastructure/gcp/gemini/searcher.go`, delete the `modelDiscovery()` accessor on `Config`.
- [x] 2.5 In `backend/internal/infrastructure/gcp/gemini/searcher.go`, delete the `ModelDiscovery` field from `gemini.Config` if present.
- [x] 2.6 In `backend/internal/di/provider.go`, remove the `ModelDiscovery: cfg.GCP.SearchModelDiscovery(),` line.
- [x] 2.7 In `backend/internal/di/job.go`, remove the `ModelDiscovery: cfg.GCP.SearchModelDiscovery(),` line.
- [x] 2.8 In `backend/pkg/config/config_test.go`, remove or update any test case referencing `GeminiSearchModelDiscovery`, `SearchModelDiscovery`, or `GCP_GEMINI_SEARCH_MODEL_DISCOVERY`. (No such references existed; no-op.)
- [x] 2.9 Run `go vet ./...` and confirm it stays clean.
- [x] 2.10 Run `make check` (or equivalent: vet + unit tests) and confirm it stays clean. (Lint clean; `pkg/config` and `internal/infrastructure/gcp/gemini` unit tests pass. `internal/infrastructure/database/rdb` integration tests fail with `events.title` column missing — pre-existing schema/migration drift on this worktree, unrelated to this change; verified by re-running with my edits stashed.)
- [x] 2.11 (added during apply) Flip default model bindings to match the spec: `defaultSearchModelExtract = "gemini-3.5-flash"`, `defaultSearchModelParse = "gemini-3.1-flash-lite"` (previously flipped under the three-step assumption). Drop the `SearchModel()` legacy fallback inside `SearchModelExtract()` / `SearchModelParse()` per the gemini-searcher-config spec.
- [x] 2.12 (added during apply) Remove unused `promptTemplateParse` constant and `urlContextMaxURLs` constant from `searcher.go`; replace `fmt.Sprintf(promptTemplateParse, string(payload))` with `string(payload)` directly. Remove unused `stepSwitchingHandler` test helper from `searcher_test.go`. Add `_ = f.Close()` wrappers in `cmd/analyze-ab-errors/main.go`, `cmd/analyze-missed-events/main.go`, `cmd/replay-ab-log/main.go` to silence `errcheck`. Format four cmd/abeval-related files that were out of sync with `gofmt`.

## 3. Refresh the cookbook-side documentation

`backend/docs/gemini-concert-searcher-tuning.md` currently describes the two-pass and three-step proposals. Rewrite it around the shipped grounded-extract architecture.

- [x] 3.1 Replace the top-level architecture section with a description of the two-step grounded-extract + JSON-coerce flow. (No existing arch section in the reference doc; added as new §10 "Concert Search Pipeline (shipped architecture)" with the call-flow diagram and inline narrative covering both LLM steps.)
- [x] 3.2 Document the three parallel Step 1 slices, including the month-offset table. (§10.2 — `tours_near` / `tours_far` / `standalones` rows with from/to offsets and the windows they cover.)
- [x] 3.3 Document the tool-set invariants per step (`step1_grounded` = `{GoogleSearch, URLContext}` + no schema; `step2_parse` = no tools + `responseJsonSchema`). (§10.2 last paragraph + §10.5 table; both reference `assertStepInvariants`.)
- [x] 3.4 Document the page-context year-inference rule and the SUPER BEAVER fixture as the canonical case study. (§10.4 — rule + SUPER BEAVER 16/28 → 28/28 recall walkthrough.)
- [x] 3.5 Document the `(local_date, venue, start_time)` dedup key and the BRADIO Billboard Live 1st/2nd-stage example. (§10.6 — rule + 4-row Billboard table + recall delta vs the 2-key alternative.)
- [x] 3.6 Add a "Historical alternatives considered" appendix summarising the abandoned two-pass and three-step designs with one-paragraph each on why they were withdrawn. (§10.8 — three paragraphs covering two-pass, three-step, and grounded-extract.)
- [x] 3.7 Update the model-selection guidance to show `extract = gemini-3.5-flash`, `parse = gemini-3.1-flash-lite` as defaults, with the documented bug references for lite + URLContext. (§10.7 — field/env-var/default table plus the "Why flash on Step 1" / "Why lite on Step 2" paragraphs citing #2120, #3513, Forum 107050.)

## 4. Re-run the 4-artist smoke against the post-cleanup code

Confirm the dead-code removal in Section 2 is behaviour-preserving.

- [x] 4.1 Run `GEMINI_AB_EVAL_SMOKE=1 GEMINI_AB_EVAL_ARTISTS=UVERworld` and confirm `discovered_count` is 2. (2026-05-24 post-cleanup smoke: `discovered_count=2`, $0.18, 35 s.)
- [x] 4.2 Run `GEMINI_AB_EVAL_SMOKE=1 GEMINI_AB_EVAL_ARTISTS=Vaundy` and confirm `discovered_count` is 43. (Post-cleanup smoke: `discovered_count=43`, $0.37, 114 s.)
- [x] 4.3 Run `GEMINI_AB_EVAL_SMOKE=1 GEMINI_AB_EVAL_ARTISTS=BRADIO` and confirm `discovered_count` is 19 and the two Billboard 2nd-stage shows survive dedup. (Post-cleanup smoke: `discovered_count=19`, $0.20, 77 s.)
- [x] 4.4 Run `GEMINI_AB_EVAL_SMOKE=1 GEMINI_AB_EVAL_ARTISTS="SUPER BEAVER"` and confirm `discovered_count` is 28 and the 12 early-2027 dates are present with `2027-MM-DD` `local_date` values. (Post-cleanup smoke: `discovered_count=28`, $0.27, 66 s.)

## 5. Commit, archive, and follow-up tracking

- [ ] 5.1 Commit the Section 2 dead-code removal under `chore(infra/gemini): drop unused ModelDiscovery config plumbing` with `Refs: #303`.
- [ ] 5.2 Commit the Section 3 doc refresh under `docs(infra/gemini): rewrite tuning doc around grounded-extract architecture` with `Refs: #303`.
- [ ] 5.3 If `make check` passes, prepare a PR with all related commits (`84f7399`..plus the two cleanup commits) for the `evaluate-gemini-search-model` branch.
- [ ] 5.4 Open follow-up tickets for the out-of-scope items called out in the proposal's Non-Goals: (a) 対バン discovery for guest appearances, (b) overseas venue timezone extraction, (c) production cost optimisation.
- [ ] 5.5 Run `/opsx:verify redesign-concert-searcher-grounded-extract` and confirm zero CRITICAL issues remain.
- [ ] 5.6 Run `/opsx:archive redesign-concert-searcher-grounded-extract` once `openspec status` reports `isComplete=true`.
