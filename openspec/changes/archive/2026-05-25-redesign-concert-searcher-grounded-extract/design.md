## Context

The `ConcertSearcher` design has gone through three iterations on this worktree:

1. **Two-pass (`redesign-concert-searcher-two-pass`, draft, withdrawn)**: lite × `URLContext` + `responseJsonSchema` in a single Pass 2 call. A 12-cell matrix on 2026-05-22 (Vaundy + BRADIO) hit invalid-JSON truncation in 8/12 cells (`{"standalones":[],"tours":` cutoff at ~33 chars of structured output). The same Pass 2 on `gemini-3.5-flash` ran clean but at ~$0.27 per artist, well above the ¥1,500 (~$10) monthly cap target.
2. **Three-step (`redesign-concert-searcher-three-step-pipeline`, draft, withdrawn)**: split into Step 1 lite-Search → Step 2 lite-URLContext → Step 3 flash-schema, expecting lite to handle the two cheap grounded calls. Two reliability defects falsified that assumption:
   - `python-genai` #2120 — lite returns empty `grounding_chunks` ~10% of the time, defeating downstream URL filtering.
   - `genkit` #3513 / Google AI Forum 107050 — lite's `URLContext` resolves the tool ~10% short of advertised; the missed URLs surface as hallucinated content with no provenance.
   We reproduced both on 2026-05-23 with UVERworld and BRADIO single-cell smokes.
3. **Grounded-extract (this change, shipped on this worktree, commits `84f7399`..`bfbcf31`)**: keep flash on the grounded call, collapse URL discovery and verbatim extraction into a single Gemini call with both `GoogleSearch` and `URLContext` enabled together, lift verbatim fields into Go, and run lite only on a pure text-to-JSON coercion step with `responseJsonSchema` (no tools, no URL retrieval).

The Gemini API officially supports combining `GoogleSearch + URLContext` per the [cookbook grounding sample](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Grounding.ipynb). On flash, the combination is reliable; the cookbook itself uses `gemini-3.5-flash` for URLContext examples and does not exemplify lite.

Smoke evidence from 2026-05-24 (this session, 4 artists × 1 cell each, default model config):

| Artist | In-scope fixture | Discovered | Date+time match | Recall | Precision | Cost | Latency |
|--------|-------------------|------------|------------------|--------|-----------|------|---------|
| UVERworld | 2 | 2 | 2 | 100% | 100% | $0.10 | 42 s |
| Vaundy | 43 | 43 | 40 (43 date-level) | 93% (date 100%) | 100% | $0.29 | 95 s |
| BRADIO | 22 | 19 | 19 | 86% | 100% | $0.21 | 76 s |
| SUPER BEAVER | 28 | 28 | 28 | 100% | 100% | $0.22 | 75 s |
| **Total** | **95** | **92** | **89 strict** | **96.8% (date+time effective)** | **100%** | **avg $0.21** | **avg 72 s** |

The three strict misses on Vaundy are Hong-Kong / Korea venue timezone extractions (`+08:00` shows extracted without a time); the three misses on BRADIO are 対バン (multi-artist co-bills) where BRADIO appears as a guest — both out of scope for this change.

## Goals / Non-Goals

**Goals:**

- Record the shipped two-step architecture as the canonical spec so future contributors do not chase the abandoned three-step or two-pass designs.
- Capture the design decisions that the evaluation surfaced: flash-on-Step-1, combined `{GoogleSearch, URLContext}`, three parallel slices, Go-side verbatim parse, `(local_date, venue, start_time)` triple-key dedup, page-context year inference.
- Remove the dead `ModelDiscovery` config plumbing without breaking the env-var contract for `ModelExtract` / `ModelParse`.
- Keep the public `Search` / `SearchExt` signatures and `SearchNewConcerts` RPC behaviour byte-identical.

**Non-Goals:**

- **Discovery of multi-artist co-bills (対バン) where the target artist is a guest.** BRADIO's missed Orangeee's Night and LIGHT YOU dates fall here. A future change MAY extend Step 1 search queries with `<artist> 出演 ライブ` / `<artist> 対バン` patterns.
- **Overseas venue timezone extraction.** Vaundy's HK and KR venues lose `start_time` (Step 1 emits the date but not the time-with-offset). A future change MAY add per-country timezone fallback inside Step 2's coercion.
- **Production cost optimisation.** This change ships an architecture that costs ~$0.20 / artist, above the ¥1,500 monthly cap target at the planned 1000 artists / day. Production tuning (caching, partial-result reuse, model swap for sufficient-recall artists) is tracked separately.
- **Two-pass and three-step migrations.** Those proposals never landed on disk in a merged commit; this change supersedes them by removal rather than migration.

## Decisions

### D1. Flash on Step 1, not lite

**Decision**: Step 1 uses `gemini-3.5-flash` by default (`defaultSearchModelExtract`). The `Config.ModelExtract` field is mandatory.

**Alternatives considered**:

1. Lite on Step 1 (per the three-step proposal). Rejected: ~10% URL-resolution failures + empty grounding_chunks bug + grounding hallucination.
2. Pro on Step 1. Rejected: ~5× the cost of flash with no measurable accuracy gain on our 4-artist smoke.

**Rationale**: flash is the cheapest model that handles `URLContext` reliably and is the only model the cookbook examples use for the `GoogleSearch + URLContext` combination.

### D2. Lite on Step 2, not flash

**Decision**: Step 2 uses `gemini-3.1-flash-lite` by default (`defaultSearchModelParse`). The Step 2 call has no tools and `responseJsonSchema` set.

**Alternatives considered**:

1. Flash on Step 2. Rejected: ~3× the cost for a task that has no semantic ambiguity (pure text-to-JSON coercion of `admin_area` + ISO date/time).
2. Lite-Pro fallback (try lite, retry on flash on truncation). Rejected: adds latency, masks the symptom rather than the root cause. Lite's truncation bug is on the `URLContext + schema` combination only; with no tools, lite handles `responseJsonSchema` reliably.

**Rationale**: the `responseJsonSchema × URLContext` truncation bug is documented to occur only when both are present. Step 2 has no tools, so the bug does not apply.

### D3. Combined `{GoogleSearch, URLContext}` in Step 1

**Decision**: Step 1's `Tools` MUST contain both `GoogleSearch` and `URLContext`. The Step 1 invariant guard rejects any other tool set.

**Alternatives considered**:

1. `GoogleSearch` only on Step 1, `URLContext` only on Step 2 (the three-step shape). Rejected — see Context.
2. `URLContext` only with the official site URL hard-coded into the prompt. Rejected: misses tour announcement pages and ticketing-site detail URLs that the model finds via search.

**Rationale**: the cookbook sample (`Search_Grounding.ipynb`) shows the combination is officially supported on flash. Discovery and extraction share the same reasoning context, so collapsing them avoids a second API round trip without sacrificing quality.

### D4. Three parallel slices

**Decision**: Step 1 fans out into three concurrent Gemini calls — `tours_near` (`from`..`from+12mo`), `tours_far` (`from+12mo`..`from+24mo`), `standalones` (`from`..`from+24mo`) — using `sync.WaitGroup`. Each slice gets its own system instruction (tour vs standalone) and its own from/to dates substituted into a workflow-style prompt.

**Alternatives considered**:

1. Single Step 1 call covering all 24 months. Rejected during the 2-slice consolidation experiment: model emitted "draft + final" chain-of-thought into the response text and doubled candidate counts.
2. More slices (e.g. quarterly buckets). Rejected: marginal recall gain, 4× cost.
3. Single tour slice (collapse near + far). Acceptable; chosen split is conservative because some artists announce 18-month-out tours (Vaundy ASIA TOUR 2027) and we want the model to focus per-slice.

**Rationale**: narrow scoping per slice reduces output truncation and lets the model commit to one bucket at a time. Cross-slice duplicates are handled by Step 2's dedup.

### D5. XML envelope shape — `<extracted>` → `<tour>` / `<standalone>` blocks with `<title>`, `<source_url>`, and `<event>` children

**Decision**: the Step 1 envelope is

```xml
<extracted>
  <tour>
    <title>...</title>
    <source_url>...</source_url>
    <event>
      <venue>...</venue>
      <country>...</country>
      <local_date>...</local_date>
      <open_time>...</open_time>
      <start_time>...</start_time>
    </event>
    <event>...</event>
  </tour>
  <standalone>
    <title>...</title>
    <source_url>...</source_url>
    <event>...</event>
  </standalone>
</extracted>
```

`<source_url>` is a child of `<tour>` / `<standalone>`, not the parent wrapper. Each `<standalone>` carries exactly one `<event>`. Field values are verbatim text from the fetched page; empty values are emitted as empty elements (`<open_time></open_time>`), never as `null` and never omitted.

**Alternatives considered**:

1. Outer `<source url="...">...</source>` wrapper (the original two-pass shape). Rejected: the dedup priority instruction in the earlier prompt drove the model to collapse every tour under the artist's homepage URL (observed in BRADIO 2026-05-23 smoke). Putting `<source_url>` inside `<tour>` lets the model pick the most detailed URL per tour.
2. JSON envelope from Step 1. Rejected: `responseJsonSchema` on flash + `URLContext` is supported but the schema must include `index` / venue strings the model is asked to copy verbatim; XML lets us treat the envelope as semi-structured text and parse with `encoding/xml`, sidestepping schema field-name policing on a step where the model already has plenty to do (search + fetch + extract).

### D6. Go-side verbatim parse for `title`, `source_url`, `venue`, `country`

**Decision**: `parseStep1Envelope` (in `searcher.go`) extracts `title` / `source_url` / `venue` / `country` from the Step 1 XML directly. Step 2's input contains only `index`, `venue`, `country`, raw `local_date`, raw `start_time`, raw `open_time`. Step 2's output contains only `index`, coerced `admin_area`, coerced ISO `local_date` / `start_time` / `open_time`.

**Rationale**: it is structurally impossible for Step 2 to hallucinate a venue or source URL it never receives. Title decoration (e.g. "(Special Edition)" appended by lite) is also eliminated.

**Trade-off**: title / source_url errors must be caught upstream, in Step 1. The cookbook-grounded flash call has not produced such errors in our smokes.

### D7. `(local_date, venue, start_time)` triple-key dedup

**Decision**: `parseStep2Response` deduplicates concerts by the tuple `(local_date, venue, start_time)`. Two shows with identical `(local_date, venue)` but different `start_time` (e.g. Billboard Live 1st stage 18:00 / 2nd stage 21:00) survive as distinct entries.

**Alternatives considered**:

1. `(local_date, venue)` only. Rejected — fold the 1st / 2nd stage pair into one row (observed on BRADIO Billboard OSAKA 2026-08-07 and TOKYO 2026-08-09).
2. `(local_date, venue, start_time, title)`. Rejected — title differences on the same physical concert (`"BRADIO Billboard Live 2026｜大阪"` vs `"BRADIO Billboard Live 2026 OSAKA"`) would defeat the dedup.

### D8. Page-context year inference rule

**Decision**: Step 1's system instruction REQUIRES the model to infer the year from page context (tour title year range, page heading) when the source page emits a partial date (e.g. `01.16. sat`). The model SHALL prefix the verbatim raw value with the inferred year, producing `2027.01.16. sat`.

**Rationale**: Step 2's lite-side coercion has no `from_date` reference and defaults year-less dates to the current calendar year. Without this rule, SUPER BEAVER's `都会のラクダ TOUR 2026-2027` page lost all 12 of its 2027 dates (they coerced to 2026, fell before the past-date cutoff, and were filtered). With the rule, SUPER BEAVER's recall went from 16/28 → 28/28 in the 2026-05-24 follow-up smoke.

**Alternative considered**: pass `from_date` into Step 2's system instruction so lite can do the inference. Rejected for now: flash has full page context (tour title, heading, etc.) and infers cleanly; lite would have to guess from a JSON array. Could be added as a belt-and-braces second layer in a future change.

### D9. Workflow-style Step 1 instructions in Japanese

**Decision**: both tour and standalone system instructions follow the same five-step numbered workflow:

1. discover (search + URL Context fetch)
2. extract into the per-field XML
3. dedup on `(venue, local_date, start_time)`
4. MECE check (all dates covered, no overlap)
5. emit XML only — no prose

Instructions are written in Japanese (the target language of most of the source pages); the prompts that fill in artist / dates are also Japanese.

**Rationale**: numbered workflows outperform rule lists on LLM compliance per OpenAI / Anthropic prompt-engineering guides. Japanese matches the source corpus.

## Risks / Trade-offs

- **[Loss of multi-source cross-validation signal]** → Mitigation: model already collapses sources internally (BRADIO 2026-05-23 smoke confirmed); no existing code consumes cross-source signals. We accept the loss in exchange for prompt simplicity and a stricter source_url contract.
- **[Cost per artist ~$0.20 exceeds the ¥1,500 monthly cap at 1000 artists/day]** → Mitigation: production deployment is gated on a separate cost-tuning change. Smoke / matrix work runs against the dev API key and stays within manual cap raises.
- **[Cross-slice tour duplicates on the 12-month boundary]** → Mitigation: `parseStep2Response`'s `(local_date, venue, start_time)` dedup folds them.
- **[Year inference can mis-attribute dates if the tour title has multiple years]** → Mitigation: the smoke harness scans for events with year < `from_date.year` or > `from_date.year + 2` and flags them. No false attributions observed in 2026-05-24 SUPER BEAVER run.
- **[Lite truncation on Step 2 if event count gets large]** → Mitigation: the schema is event-array shaped; each event coerced contributes ~30 tokens of output, so even 100 events fit under the 16 384-token cap with headroom. The largest observed run (Vaundy, 43 events) consumed 2 146 candidates tokens, ~13% of the cap.

## Migration Plan

This change is **additive on the spec side** and **already shipped on the code side** (the architecture is on disk in commits `84f7399`..`bfbcf31`). No production migration is required.

Spec migration:

1. Land this change (proposal / design / specs / tasks) on the `evaluate-gemini-search-model` branch.
2. Apply the implementation tasks — the only code work remaining is the dead-code removal in `pkg/config/config.go`, `internal/di/{provider,job}.go`, and the corresponding `config_test.go` cleanup; everything else is already shipped.
3. Rewrite `backend/docs/gemini-concert-searcher-tuning.md` around the two-step shipped flow.
4. Run a final 4-artist smoke against the post-cleanup code to confirm the dead-code removal is behaviour-preserving.
5. Update the existing `openspec/specs/` if any concert-search capability there references the abandoned three-step shape (none observed in the 2026-05-24 audit).

Rollback strategy:

- `git revert` the code commits in reverse order. The public RPC contract is unchanged, so no DB or proto rollback is needed.
- The removed `ModelDiscovery` field can be restored by reverting the dead-code-removal commit; existing deployments that did not set `GCP_GEMINI_SEARCH_MODEL_DISCOVERY` will continue to work either way.

## Open Questions

- **Q1**: Should `parseStep2Response`'s `(local_date, venue, start_time)` dedup also fall back to `(local_date, venue)` when `start_time` is empty on both sides? Currently empty `start_time` on both sides counts as equal (correct — they ARE the same event). No action needed unless a future fixture surfaces a counter-example.
- **Q2**: The 24-month upper bound on `tours_far` and `standalones` is arbitrary; some artists announce 30-month-out residencies. Out of scope for this change but worth tracking.
- **Q3**: Step 2's `admin_area` description requests local form ("愛知県") but lite has been observed emitting ISO 3166-2 codes ("JP-23") when the input venue carries a prefecture prefix. Tracked separately; not blocking this spec.
