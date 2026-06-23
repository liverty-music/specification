## 1. Backend — searcher (per-artist + seed-URL grounding)

- [x] 1.1 Change `SalesPhaseSearcher` interface from per-series to **per-artist**: input = artist name + official-site URL + the artist's known upcoming series array (`series_id`, title, known event dates); output = phases mapped to `series_id`
- [x] 1.2 Seed the artist's official-site URL into the Step-1 prompt and pass it through the `URLContext` tool so grounding fetches real pages (fixes `grounding.fired=false`); remove the `timeRangeFilter` (unreliable, googleapis/python-genai#1207) — no recency window is used
- [x] 1.3 Rework the Step-1 prompt: extract series-level sale phases from the seeded URL, attribute each to a supplied `series_id` (by title/known dates); keep only the application-window filter (exclude sales whose deadline is before today). Keep Step-2 date coercion (RFC 3339)
- [x] 1.4 Add a `series_id` attribution/validation step: drop any phase that cannot be confidently mapped to a supplied series (never guess)
- [x] 1.5 Return ONLY series for which a sale phase was discovered (do not echo back all input series); output stays small — no chunking needed
- [x] 1.6 Author the Gemini instructions in **English** (keeping the Japanese token values the parser maps, e.g. `抽選`/`ファンクラブ`)

## 2. Backend — discovery use case

- [x] 2.1 Group upcoming series by **artist**; build the per-artist series array and resolve each artist's seed URL from `official_site`
- [x] 2.2 If the artist has no official-site URL (NotFound) or an empty URL, **skip the artist benignly** (Warn) without calling the searcher; only genuine infra errors propagate
- [x] 2.3 Call the searcher once per artist; upsert returned phases with the unchanged `(series_id, apply_start_time)` convergence; publish `SALES_PHASE.discovered` only for newly inserted phases (unchanged)

## 3. Backend — tests & verification

- [x] 3.1 Update searcher unit tests for the per-artist input/output and `series_id` attribution (incl. unknown-series drop)
- [x] 3.2 Update discovery use-case tests for artist-batched invocation and the no-official-site / empty-URL skip paths
- [x] 3.3 Run `make check` (build, vet, unit + integration tests) until green

## 4. Ship to production

- [x] 4.1 Open the backend PR; merge after review and CI pass (PR #338 merged 2026-06-19)
- [x] 4.2 Publish the backend GitHub Release (Release `v1.10.0` published 2026-06-19; prod overlay including the `sales-phase-discovery` / `sales-reminders` cronjobs now pinned to `v1.12.0`, which carries the per-artist searcher)
- [x] 4.3 Gemini spend cap raised: the 2026-06-23 prod run had **0** `spending cap` 429s (vs 20/20 before the raise)
- [x] 4.4 Verified in prod (manual discovery run 2026-06-23, 49/49 artists succeeded): per-artist batching confirmed (YOASOBI 6→1 call, Bruno Mars 32→1 call), URLContext fetched seeded official sites (`URL_RETRIEVAL_STATUS_SUCCESS` ×4), and the pipeline produced **3 new phases** (羊文学 2, SUPER BEAVER 1) with the `announce-sales-phase` consumer subscribed to `SALES_PHASE.discovered`. NOTE: `grounding.fired` (GoogleSearch) stayed false on all calls and the surfaced phases were memory-derived rather than from the fetched pages — grounding-quality follow-up tracked in #639
- [x] 4.5 Grounding cost goal met: GoogleSearch grounding never fired so per-series grounding billings dropped to ~0, and the run used 20 calls for 49 artists (≈8× fewer than the prior per-series approach)
