## Context

The sales-phase searcher discovers ticket-sale windows for the upcoming series of followed artists. It currently runs a two-step Gemini pipeline **per series**: Step 1 is a grounded extract (`gemini-3.1-flash-lite`, tools = `GoogleSearch` + `URLContext`, thinking=high) returning a verbatim XML envelope; Step 2 coerces dates to RFC 3339. Production telemetry (2026-06-18 run) exposed two structural failures:

1. **Grounding never fires.** All 99 calls logged `grounding.fired=false`, `tool_use≈0`, and produced 0 final phases. Per Google's docs, when `GoogleSearch` + `URLContext` are combined the model first answers from its own knowledge or a *provided* URL and only falls back to Google Search if it cannot. We enable `URLContext` but pass **no URL**, so the model answers from memory (hallucinated or empty) and Search never fires. `timeRangeFilter` is also unreliable (known bug python-genai #1207).
2. **Cost scales with series, not artists.** One grounded billing per series (~$0.035 each) × 99 series ≈ the ¥637 spike, and series fragmentation (one Bruno Mars tour = 31 `series_id`s) multiplies it for zero added value.

The rest of the feature (series-level `SalesPhase`, `(series_id, apply_start_time)` convergence, `Tracking`-journey audience, KEDA delivery) is shipped and correct; it just starves because discovery yields nothing.

## Goals / Non-Goals

**Goals:**
- Make grounding actually fire by seeding the artist's official-site URL into `URLContext`.
- Cut grounding billings ~8× by batching one Gemini call per artist instead of per series.
- Use no recency window at all (no `timeRangeFilter`, no announcement-date cutoff) — only the application-window filter; re-reading the live official site is safe under the idempotent upsert.
- Preserve the shipped series-level model, upsert convergence, audience, and KEDA wiring unchanged.

**Non-Goals:**
- No protobuf/BSR change (`SalesPhase` entity is unchanged; the searcher is backend-internal).
- No duplicate-series dedup (separate session). Artist batching mitigates its cost but does not fix fragmentation.
- No change to the series-level `SalesPhase` shape, the `(series_id, apply_start_time)` upsert, the `Tracking`-journey audience, or notification content.

## Decisions

### D1. One Gemini call per artist, with the artist's series passed as input

`SalesPhaseSearcher` changes from `SearchSalesPhases(artistName, seriesTitle, seriesID)` to a per-artist call that receives the artist plus an array of that artist's known upcoming series (`series_id`, title, known event dates). The structured output is an array of `{ series_id, phases[] }`; the model attributes each discovered sale to the correct `series_id` using the supplied titles/dates. The discovery use case groups upcoming series by artist (it already lists concerts per artist) and calls the searcher once per artist.

- **Why:** an artist's official/FC/play-guide pages list all their tours together, so one grounded fetch per artist is both cheaper (99 → ~12 grounded billings) and more natural for grounding. It also collapses fragmented duplicate series into one call.
- **Alternative — keep per-series, add caching:** rejected; still pays per-series grounding and does not address fragmentation.
- **Disambiguation:** the model maps phases to `series_id` from the input array (title + known dates). A phase it cannot confidently map is dropped (never guessed onto a wrong series).

### D2. Seed the official-site URL into URLContext to force real grounding

Pass the artist's official-site URL (from the artist's `official_site`) in the prompt and instruct the model to extract ticket-sales info from that page (and linked ticketing pages). With a concrete URL, `URLContext` fetches real content instead of the model answering from memory.

- **Why:** matches the documented combined-tool behavior — provide the URL so the model reads it rather than falling through to (non-firing) memory.
- **URL availability:** when an artist has no official_site URL (or an empty one), skip the artist benignly (Warn) without calling the searcher — no grounding seed means no value, and the followed-artist set is not guaranteed to all have a site.
- **`timeRangeFilter`:** keep it off / best-effort only; do not depend on it (buggy). Recency is a prompt instruction.

### D3. No recency window — re-read the live official site every run

The searcher does NOT filter by announcement date and does NOT use `timeRangeFilter`. The only date filter is the **application window** ("exclude sales whose application deadline is before today"), a correctness requirement (don't surface dead sales), not a freshness optimization.

- **Why no incremental window:** the official site read via URLContext is a **live full-state source**, not a delta feed — an announcement-date filter would only trim the OUTPUT, not what is fetched. The dominant cost (grounding requests) is already solved by per-artist batching (D1), and the `(series_id, apply_start_time)` upsert is idempotent + last-write-wins, so re-reading the same phases every run is safe (no duplicate announcement). A hard cutoff would add a permanent-suppression risk (a phase missed once could fall outside the window forever) for negligible token savings.
- **Considered and dropped — persisted per-artist last-searched timestamp + overlap margin:** rejected as unnecessary complexity (no search-log table, no `since`, no margin). Revisit only if output-token cost is later shown to matter, as a soft "prioritize new" hint rather than a hard cutoff. Both `timeRangeFilter` and a prompt `since` implement the same axis; neither is used.

### D4. No proto change; keep everything downstream identical

The searcher's input/output are backend-internal. `liverty_music.entity.v1.SalesPhase`, the `(series_id, apply_start_time)` upsert, the `Tracking`-journey audience, and KEDA wiring are untouched.

- **Why:** this is a discovery-efficiency/efficacy change, not a contract change.

## Risks / Trade-offs

- **Artist-batched call must correctly attribute phases to `series_id`** → mitigated by passing titles + known dates and dropping unmappable phases (never guess).
- **Larger prompt/response per call** (all series for an artist) → watch `MaxOutputTokens` (currently 16384); chunk an artist with many series if needed.
- **Grounding may still under-fire even with a URL** (model/SDK behavior) → verify in prod with the cap raised; if so, escalate model (flash-lite → flash) as a follow-up.
- **Prod verification needs the Gemini spend cap genuinely raised** (the prior raise did not take effect; project is at ¥2,292/¥2,000).

## Migration Plan

1. **backend**: refactor `SalesPhaseSearcher` to per-artist (new input/output schema, URL seeding, prompt rework, drop `timeRangeFilter` dependence); update the discovery use case to group by artist and skip artists without an official-site URL; update unit tests; `make check`.
2. Open the backend PR; merge after CI; release `v1.10.0`; confirm the auto pin-bump (and the sales cronjobs) move to `v1.10.0`.
3. **Prod verification** (cap raised): a discovery run grounds (>=1 `grounding.fired=true`), yields phases for tracked artists' series, publishes `SALES_PHASE.discovered`, KEDA scales the consumer, and a `Tracking` fan receives the announcement; confirm grounding billings dropped to ~1/artist.
4. **Rollback**: revert the backend change; no schema or proto dependency downstream.

## Resolved Decisions

- **Recency window**: none. No `timeRangeFilter`, no announcement-date cutoff, no search-log table — only the application-window filter. (The incremental-window idea was dropped as unnecessary; see D3.)
- **Seed URL**: resolved from the artist's `official_site`; an artist without one (or with an empty URL) is skipped benignly (the searcher is not called).
- **Output size / chunking**: the searcher returns ONLY series for which a phase was discovered (it does not echo back all input series), so the output stays small and no per-artist chunking is required.
