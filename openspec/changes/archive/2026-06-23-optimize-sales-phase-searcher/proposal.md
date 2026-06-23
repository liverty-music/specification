## Why

The sales-phase searcher is both **expensive and ineffective** in production. It fires one grounded Gemini call **per series**, and prod analysis of the 2026-06-18 run showed 99 series → 99 GoogleSearch grounding billings (~¥637 for that single run) with `grounding.fired=false` on every call and **0 phases produced**. The root cause is confirmed against Google's docs: `URLContext` is enabled but no URL is ever passed, and Google Search only fires as a *fallback* when the model cannot answer from its own knowledge or a provided URL — so the model answers from memory and never grounds. Cost is further multiplied by series fragmentation (e.g. one Bruno Mars tour split across 31 `series_id`s, each separately billed).

The downstream pipeline (series-level `SalesPhase`, `(series_id, apply_start_time)` convergence, `Tracking`-journey audience, KEDA-driven consumer delivery) is already shipped and correct — it just never receives real phases because discovery produces nothing. Fixing the searcher is the last missing piece for fans to actually receive sale notifications.

## What Changes

- **Artist-level batching**: replace the per-series Gemini call with **one call per artist**. The call receives the artist plus the artist's known upcoming series as an array (`series_id`, title, known event dates) and returns discovered sale phases mapped back to the correct `series_id`. This cuts grounding billings ~8× (99 → ~12) and collapses duplicate/fragmented series into a single call.
- **Real grounding via seed URL + URLContext**: pass the artist's official-site URL into the prompt so `URLContext` fetches actual pages, and instruct the model to extract ticket-sales information from that source. This fixes `grounding.fired=false` / 0 results. An artist without a usable official-site URL is skipped (no seed → no value).
- **No recency window**: drop `timeRangeFilter` (unreliable; known bug python-genai #1207) and use no announcement-date cutoff at all. The official site is a live full-state source and the `(series_id, apply_start_time)` upsert is idempotent, so re-reading every run is safe; only the application-window filter (exclude already-closed sales) applies. Gemini instructions are written in English.
- Keep the series-level `SalesPhase` model, `(series_id, apply_start_time)` upsert convergence, `Tracking`-journey audience, and KEDA wiring exactly as shipped.

## Capabilities

### New Capabilities
<!-- None: this change modifies the existing sales-phase-discovery capability only. -->

### Modified Capabilities
- `sales-phase-discovery`: the searcher changes from one grounded call **per series** to one grounded call **per artist**, taking the artist's known series as input and returning phases mapped to each `series_id`; grounding is driven by a seeded official-site URL through `URLContext` (not memory); no recency window is used (no `timeRangeFilter`, no announcement-date cutoff) and an artist without a usable official-site URL is skipped. The discovery upsert, series-level model, and announcement audience are unchanged.

## Impact

- **Backend**: `SalesPhaseSearcher` interface + Gemini implementation (per-artist call, English prompt, per-phase `series_id` attribution against the supplied series, URL seeding via the artist's official site, remove `timeRangeFilter`); discovery use case (group upcoming series by artist, resolve the seed URL, skip artists without one); unit tests.
- **Database**: none (no new table or migration).
- **cloud-provisioning**: no manifest change expected (same cronjob); confirm config keys (models/thinking) still apply.
- **No protobuf/BSR change**: the searcher interface and entities are backend-internal; `liverty_music.entity.v1.SalesPhase` is unchanged.
- **Cost/efficacy**: ~8× fewer grounding billings AND non-zero phase yield, so the already-wired discovery → announce/reminder → KEDA → delivery path finally produces real notifications to `Tracking` fans. (Prod verification requires the Gemini spend cap to be genuinely raised.)
- **Out of scope**: duplicate-series dedup is investigated in a separate session; artist-level batching mitigates its cost impact but does not fix the underlying fragmentation.
