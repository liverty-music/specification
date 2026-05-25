## Why

Two prior redesigns (`redesign-concert-searcher-two-pass`, `redesign-concert-searcher-three-step-pipeline`) hypothesised that `gemini-3.1-flash-lite` could carry the URL-grounded portion of concert search cheaply. Empirical smoke evidence on this worktree falsified both:

- `responseJsonSchema` × `URLContext` on lite truncated ~67% of cells (`{"standalones":[],"tours":` cutoff) — confirmed in the 2026-05-22 12-cell run.
- Lite's `URLContext` tool has documented reliability defects (python-genai #2120 empty `grounding_chunks`, genkit #3513 ~10% tool-resolution failures, Google AI Forum 107050 grounding hallucination) — observed directly in our 4-artist smokes.

The shipped architecture (commits `84f7399`..`bfbcf31`) keeps `gemini-3.5-flash` on the grounded extract step, collapses URL discovery and verbatim extraction into a single Gemini call with both `GoogleSearch` and `URLContext` enabled together, lifts title / source_url / venue / country verbatim into Go, and runs `gemini-3.1-flash-lite` only on a pure text-to-JSON coercion step (no tools, schema enforced). A 4-artist smoke (UVERworld, Vaundy, BRADIO, SUPER BEAVER — 95 in-scope events) records **92 / 95 effective matches at 100% precision, ~$0.20 / artist, ~75 s / artist** end-to-end. The "effective" qualifier matters: Vaundy is counted at date level (43 / 43) so its three HK / KR time-zone misses don't show as misses; the strict (date + time) total for the same run is **89 / 95 (93.7%)**. design.md's smoke table breaks the two figures out per artist.

This change records that architecture as the new spec so future work has a single source of truth.

## What Changes

- **BREAKING (internal contract)** — `ConcertSearcher.Search` executes **two** Gemini calls per invocation, not three:
  - **Step 1 — Grounded extract (`gemini-3.5-flash` + `{GoogleSearch, URLContext}` + no schema)**: fans out into three parallel slices (`tours_near` `[from, from+12mo]`, `tours_far` `[from+12mo, from+24mo]`, `standalones` `[from, from+24mo]`). Each slice emits an `<extracted>` XML envelope containing per-tour or per-standalone blocks with `<title>`, `<source_url>`, and one or more `<event>` children.
  - **Step 2 — JSON coerce (`gemini-3.1-flash-lite` + `responseJsonSchema` + no tools)**: receives a JSON array of per-event raw fields (index, venue, country, raw date strings) and returns coerced `admin_area` + RFC3339 `start_time` / `open_time`. Title / source_url / verbatim venue never enter Step 2's input or schema.
- **Go-side verbatim parse**: `parseStep1Envelope` extracts title / source_url / venue / country from the Step 1 XML envelope; `mergeAndDedupEnvelopes` concatenates the per-slice `<extracted>` bodies (no URL grouping); `parseStep2Response` joins coerced fields back to the drafts by `index` and dedups on `(local_date, venue, start_time)` so 1st-stage / 2nd-stage shows at the same venue on the same day survive as distinct concerts.
- **Step 1 prompts** are workflow-style numbered procedures (discover → extract → dedup → MECE check → emit-XML), one variant per slice family (tour vs standalone). The prompts carry four positional placeholders: `from_date`, `to_date`, artist name, official-site host. The instructions are written in Japanese.
- **Page-context year inference** is required of Step 1: when a source page emits a partial date (e.g. `01.16. sat` under a "TOUR 2026-2027" tour title) the model SHALL prefix the verbatim raw value with the inferred year so Step 2's coercion has an unambiguous input. Without this, lite defaults all year-less dates to the current calendar year and the past-date filter discards forward-dated rows.
- **Config drops `ModelDiscovery`**. Only `ModelExtract` (Step 1) and `ModelParse` (Step 2) are used. The corresponding env var `GCP_GEMINI_SEARCH_MODEL_DISCOVERY`, default `defaultSearchModelDiscovery`, and DI plumbing are removed.
- **`SearchMetadata` exposes `Step1Grounded` and `Step2Parse`** (each `*PassMetadata`). `Step1Search` / `Step2Extract` / `Step3Parse` from the abandoned three-step proposal do not appear.
- The public `Search` / `SearchExt` wrappers keep their signatures and `[]*entity.ScrapedConcert` return type. The `SearchNewConcerts` RPC and the `auto-concert-discovery` CronJob are unaffected.
- The earlier `redesign-concert-searcher-two-pass` and `redesign-concert-searcher-three-step-pipeline` change proposals are removed (never committed, never archived) and superseded by this change.
- **`cmd/smoke-diff` per-event evaluation tool**: a new Go command in `backend/cmd/smoke-diff/` that consumes one A/B-harness raw artifact and the ground-truth fixture and prints a four-bucket breakdown (MATCH / MISS / FALSE_POSITIVE / TIME_MISMATCH) for a single artist. Formalises the ad-hoc `jq` + `comm` pipelines used during the 4-artist post-cleanup smoke so per-event analysis is reproducible from a single command. Implementation lands in a follow-up PR (`feat(cmd/smoke-diff)`); the requirement and tasks are recorded here so the contract is captured alongside the architecture it observes.

## Capabilities

### New Capabilities

- `gemini-grounded-extract-and-coerce`: the two-step grounded-extract / JSON-coerce pipeline, three parallel Step 1 slices, the `<extracted>` XML envelope shape, the Go-side verbatim parse, the year-inference rule, the `(local_date, venue, start_time)` dedup key, the tool-set invariants per step, the per-step `SearchMetadata` fields, and the `cmd/smoke-diff` per-event evaluation tool that consumes the resulting raw artifacts.
- `gemini-searcher-config`: per-step model configuration. Two fields — `ModelExtract` (Step 1) and `ModelParse` (Step 2) — each with a `defaultSearch*` fallback and a `GCP_GEMINI_SEARCH_MODEL_*` env var override. Default model bindings: extract → `gemini-3.5-flash`, parse → `gemini-3.1-flash-lite`. No `ModelDiscovery`.

### Modified Capabilities

<!-- None: neither capability exists in openspec/specs/ yet. -->

### Removed Capabilities

<!-- None merged. The two prior unmerged change proposals (redesign-concert-searcher-two-pass and redesign-concert-searcher-three-step-pipeline) were deleted from openspec/changes/ as part of preparing this change; their drafts of gemini-three-step-pipeline / gemini-two-pass-url-resolution / earlier gemini-searcher-config never reached openspec/specs/. -->


## Impact

- **Affected code**:
  - `backend/internal/infrastructure/gcp/gemini/searcher.go` — already on disk; this change codifies it.
  - `backend/pkg/config/config.go` — `GeminiSearchModelDiscovery` field, `SearchModelDiscovery()` helper, and `defaultSearchModelDiscovery` constant to be removed.
  - `backend/internal/di/provider.go`, `backend/internal/di/job.go` — `ModelDiscovery` wiring to be removed.
  - `backend/internal/infrastructure/gcp/gemini/searcher_integration_test.go` — A/B harness already records `Step1Grounded` / `Step2Parse` per cell; nothing to change.
  - `backend/docs/gemini-concert-searcher-tuning.md` — to be rewritten around the two-step shipped flow; the historical three-step narrative is moved to an appendix.
- **Public RPC contract**: unchanged. `SearchNewConcerts` shape and behaviour identical.
- **Dependencies**: no new modules. Continues to use `google.golang.org/genai@v1.57.0`.
- **Cost**: per-artist API spend averages ~$0.20 in the 4-artist smoke (UVERworld $0.10, BRADIO $0.21, SUPER BEAVER $0.22, Vaundy $0.29). Above the ¥1,500 / ~$10 monthly cap target if run at production volume; production deployment is out of scope for this change and tracked separately.
- **Latency**: ~75 s end-to-end per artist with the 3 parallel slices firing concurrently; longest slice dominates.
- **Reliability**: lite's `URLContext` defects are sidestepped — lite no longer touches that tool. Flash-on-Step-1 handles grounded extraction; lite-on-Step-2 only sees plain JSON.
- **No protobuf / DB schema / RPC contract changes.**
- **Deploy artifacts**: `cloud-provisioning/k8s/backend/overlays/<env>` ConfigMaps SHOULD drop the now-unused `GCP_GEMINI_SEARCH_MODEL_DISCOVERY` key; existing `GCP_GEMINI_SEARCH_MODEL_EXTRACT` and `_PARSE` overrides continue to work.
