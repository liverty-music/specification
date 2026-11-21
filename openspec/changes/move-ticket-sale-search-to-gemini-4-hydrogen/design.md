## Context

See proposal.md - Why. `TicketSaleSearcher.SearchPublishedSales` (backend `internal/infrastructure/gcp/gemini/ticket_sale_searcher.go`) makes one grounded call per artist (Google Search limited to the last 30 days, URL context, JSON schema) with the artist's name, official site and the series to search; the system instruction (`systemInstructionPublishedSales`) states the purpose, the task, the sources (official site, official tour pages and the series' ticketing-service pages) and the never-guess rule. The model comes from `GCP_GEMINI_SEARCH_MODEL_EXTRACT`, which the base `sales-phase-discovery` ConfigMap pins to `gemini-3.8-flash` / `low` for dev and prod; `defaultPublishedSaleSearchModel` in `pkg/config` is the same. `maxOutputTokens` (65,536) is shared with the concert searcher.

The harness `TestTicketSaleSearcher_PublishedSalesEval` (`ticket_sale_eval_integration_test.go`, `GEMINI_SP_EVAL=1`) scores found / missed / extra sales and wrong values on found ones, against 5 sales captured on 2026-10-05 with the current time frozen to that date. The model reads today's pages, where those sales have opened or been removed, so the fixture no longer measures anything.

Lessons from `pass-tour-detail-pages-to-concert-search` (backend `docs/gemini-concert-searcher-tuning.md` §10.0): at thinking `low`, `gemini-4-hydrogen` answers from what it has read and stops searching; URL context opens only URLs in the request or in search results; a completion criterion in the system instruction made it look further (47/48 against 33/48 hard-to-reach dates).

## Goals / Non-Goals

**Goals:**
- Decide, on a current fixture, whether the published-sale searcher moves to `gemini-4-hydrogen` before 2027-01-01, and with which system instruction.

**Non-Goals:**
- Changing what the search returns (the spec's requirements stay as they are).
- Listing the official top page's links in the prompt, as concert search does: sales live on ticket vendor pages, which that list blocks.
- Thinking levels other than `low` (cost; `gemini-4-hydrogen` accepts nothing lower).

## Decisions

**D1. Re-capture the fixture from current pages.** Pick at least 4 artists with sales that open after the capture date, taken from prod `ticket_sales` (discovered sales whose application start is in the future) and each checked on the page that announces it: at least 10 sales in all, covering a lottery with a result date, a later round (2次 or later), and a series with two or more upcoming sales. Freeze the harness's current time to the capture time, as today. Only public pages; a sale visible only to fan-club members stays out.

**D2. Harness records the decision's inputs.** Per call: found / missed / extra and wrong values (as today), search queries (from the tool calls), input / output / thinking / tool-use tokens, cost at the 2027-01-01 price (`Pricing2027`), latency, and whether the response was empty or failed. Results are written next to the concert harness's (`testdata/ab_results/`), so the decision cites files.

**D3. Acceptance criteria.** `gemini-4-hydrogen` (thinking `low`) replaces `gemini-3.8-flash` when, over all fixture sales with 3 repetitions each:
- it finds every sale that `gemini-3.8-flash` finds in at least 2 of 3 runs, and its overall found rate is not lower;
- it returns no more wrong values and no more extra sales;
- it has no new empty responses, failures or 120 s timeouts, and p90 latency under 90 s;
- cost per call at the 2027 price is not higher.
Per-sale results are compared, not only totals: a total can hide a sale dropped every time (as concert search's run 2 did).

**D4. A completion criterion if hydrogen stops early.** When `gemini-4-hydrogen` misses sales under D3, a system instruction adding one line — every sale the official pages announce for a given series that has not opened yet is in the answer — is evaluated on it with the same criteria. The rest of `systemInstructionPublishedSales` stays: its rules are the spec's (no guessed values, no trades or resales). If neither instruction passes, the searcher stays on `gemini-3.8-flash` and the reason is recorded.

**D5. Ship model and pin together.** On adoption, `defaultPublishedSaleSearchModel` and the base `sales-phase-discovery/configmap.env` pin change in the same release window, the cloud-provisioning PR merged after the backend release that carries any new instruction (the pin alone changes the model at the next job run). The base pin covers dev and prod; dev stays stopped and unverifiable.

## Risks / Trade-offs

- [Few sales; a model can win by chance] → 3 repetitions and per-sale comparison (D3).
- [Sales open between capture and evaluation] → the harness freezes the current time to the capture time, and the runs happen within a day of the capture.
- [The completion line makes the model search more] → cost per call is part of D3; at 56 searches a month the absolute change is small.
