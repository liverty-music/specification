## Context

The concert extractor is the two-step grounded pipeline in `internal/infrastructure/gcp/gemini` (see the `gemini-grounded-extract-and-coerce` capability); the sales-phase extractor is an analogous two-step pipeline. Both are exercised by the matrix A/B harness (`searcher_integration_test.go`, `GEMINI_AB_EVAL=1`) against a frozen ground-truth fixture, scored on `(local_date, normalized_venue)`. This change was driven by (a) an A/B evaluation of a candidate model upgrade and (b) analysis of production discovery data. See proposal.md — Why.

## Goals / Non-Goals

**Goals:**
- Decide, on evidence, whether to adopt `gemini-3.7-flash` for the extract step.
- Remove the two production extraction defects that the data exposed (venue translation / weak `source_url`; play-guide-as-`一般` and missing lottery dates).
- Keep the A/B harness honest so future model/prompt decisions are measurable.

**Non-Goals:**
- Changing production `pkg/config` model / thinking / temperature defaults (the measured `low` / `0.4` optimum is recorded for a follow-up, not applied here).
- Building a sales-phase eval harness or fixture.
- Fixing series fragmentation or deprecating merch discovery (separate changes).

## Decisions

### Retain gemini-3.6-flash; do not adopt gemini-3.7-flash
A/B on a refreshed 4-artist fixture, offline re-scored to neutralize venue-string artifacts, showed **both models at 100% date-coverage recall** (equal discovery quality). `gemini-3.6-flash` and `gemini-3.7-flash` share identical token pricing (introductory $0.75 / $3.75 per 1M through 2026, both doubling in 2027), yet 3.7 consumed ~4.8× the Step 1 grounding tokens (`ToolUsePromptTokenCount`), i.e. ~1.75× the per-search cost, for no quality gain. 3.7 is ~2× faster, but concert discovery is a background job where cost dominates latency. Alternatives considered: adopt 3.7 for speed/newness (rejected — cost, no quality gain); switch the extract step to `thinking=low, temperature=0.4` now (deferred — it is the measured optimum for 3.6 but a production-behavior change best shipped on its own).

### Extract every field in the source's original language
The measured quality gap for 3.7 was an artifact of it translating Japanese venue names to English on multilingual tour sites; 3.6 exhibited a milder form (old-vs-new renamed-venue strings). The Step 1 instruction now forbids translation/romanization and mandates the Japanese form even on multilingual pages. This directly protects downstream event de-dup, `admin_area` inference, and display. Alternative: post-process/normalize venue strings Go-side (rejected — lossy, and it hides a real instruction-following defect rather than fixing it at the source).

### Prefer the tour-specific page for source_url
Production `source_url` was often the site top or a news-list page. The instruction now prefers the tour special/feature page (or specific announcement) over the top/news-list page. This is measurable via the harness `field_accuracy.source_url`. It also makes a separate merch link largely redundant (the tour page carries goods info) — motivating the deferred merch-discovery deprecation.

### Sales-phase: play-guide priority and lottery completeness
Production classified 45% of `一般` phases that actually carried a named play-guide provider; and left `lottery_result` empty on 78% of `抽選` phases. The instruction now classifies any named-play-guide sale as `プレイガイド` (reserving `一般` for non-guide direct sales) and directs the model to extract the application deadline and result date for `抽選` phases when published (never guessed).

### Harness correctness (supporting)
`gemini-3.7-flash`/`gemini-3.6-flash` pricing rows were added; a Step 1/Step 2 cost-attribution bug (Step 1 cost computed against the wrong model → $0) was fixed; venue normalization gained aliases for a renamed venue and a `某所`/TBD collapse so eval matching reflects real equivalence. The genai SDK was bumped v1.57→v1.69 (no breaking changes).

## Risks / Trade-offs

- **Sales-phase prompt changes are unmeasured.** No sales-phase eval harness exists, and their production effect is confounded by the separately-tracked series-fragmentation defect (a tour's events are minted as one series per event, duplicating every series-level attribute). They ship as reasoned, low-risk prompt improvements; verification will come with the series-grouping fix.
- **The `source_url` and native-language changes are prompt-only** and depend on the model's instruction-following; the harness measures the outcome for concert extraction but not for the sales-phase pipeline.
- **The `thinking=low, temperature=0.4` optimum is documented but not applied**, so production keeps its current (higher-cost) extract behavior until a follow-up change lands.
- Introductory model pricing doubles on 2027-01-01; cost figures here are point-in-time (2026).
