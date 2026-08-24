## Why

Analysis of production discovery data surfaced two extraction-quality defects. (1) The concert grounded-extract step translated / romanized Japanese venue names (e.g. `幕張メッセ 9・11ホール` → `Makuhari Messe Halls 9 & 11`) — especially on multilingual tour sites — which breaks event de-duplication, `admin_area` inference, and display; and it frequently stored the official-site top page or a generic news page as `source_url` instead of the tour's dedicated page. (2) The sales-phase step mis-classified play-guide sales as `一般 (GENERAL)` (45% of GENERAL rows carry a named play-guide provider such as イープラス / ローチケ / ぴあ) and left the lottery result-announcement date empty on 78% of `抽選` phases and the application deadline empty on 55% of phases. Separately, a candidate model upgrade to `gemini-3.7-flash` needed an evidence-based accept/reject decision.

## What Changes

- **Concert grounded-extract (Step 1)**: every verbatim field, and venue in particular, MUST be extracted in its original language — no translation, romanization, or localization even when a page offers an English/multilingual view; and `source_url` MUST prefer the tour-specific special/feature page (or the specific announcement article) over the official-site top page or a generic news-list page.
- **Sales-phase extract (Step 1)**: a sale conducted through a named play guide is classified `プレイガイド` (with the guide in `provider_name`) even when it is a general (non-membership) on-sale — `一般` is reserved for a general sale not tied to a named guide; and for `抽選` (lottery) phases the application deadline and the result-announcement date SHALL be extracted from the ticket page when published (never guessed).
- **Model evaluation — decision, non-BREAKING**: `gemini-3.7-flash` was A/B-evaluated against `gemini-3.6-flash` on a refreshed 4-artist ground-truth fixture. Both reach equal discovery quality (100% date-coverage recall), but 3.7 costs ~1.75× (≈4.8× grounding tokens) at identical unit pricing, so **`gemini-3.6-flash` is retained**; the measured optimum for the extract step is `thinking=low, temperature=0.4`.
- **Tooling / fixtures**: bump `google.golang.org/genai` v1.57.0 → v1.69.0; the A/B harness gains `gemini-3.7-flash` support, a Step 1/Step 2 cost-attribution fix, model pricing rows, and venue-normalization aliases (renamed venue + `某所`/TBD collapse); the ground-truth fixture is refreshed to 101 events across 4 artists with `evaluation_from = 2026-08-23`.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `gemini-grounded-extract-and-coerce`: Step 1 verbatim extraction now mandates original-language (no translation / romanization) values, and `source_url` selection prefers the tour-specific page over the site top / news-list page.
- `sales-phase-discovery`: Step 1 classification prioritizes `プレイガイド` when a named guide is present (over `一般`), and `抽選` phases extract the application-deadline and result-announcement dates when published.

## Impact

- **Code**: `internal/infrastructure/gcp/gemini/searcher.go` (Step 1 prompt), `internal/infrastructure/gcp/gemini/sales_phase_searcher.go` (Step 1 prompt), `internal/infrastructure/gcp/gemini/{searcher_integration_test.go, abeval_scoring.go, abeval_test.go}` and `testdata/*` (A/B harness + fixture), `go.mod` / `go.sum` (genai v1.69.0).
- **No API / proto / DB-schema changes and no migration.** Production `pkg/config` defaults are unchanged — `gemini-3.6-flash` remains the extract model; the `thinking=low, temperature=0.4` optimum is documented for a follow-up config tuning, not applied here.
- **Measurability**: the `source_url` prompt change is measurable via the existing A/B harness `field_accuracy.source_url`; the sales-phase prompt changes are not yet covered by an eval harness (their production effect is also confounded by the separately-tracked series-fragmentation defect).
- **Deferred to separate changes** (out of scope here): deprecating `merch-discovery` and dropping `series.merch_url` (redundant with `source_url`); and fixing series fragmentation in the persistence layer (a tour's events are minted as one series per event instead of one series per tour) plus the associated data migration.
