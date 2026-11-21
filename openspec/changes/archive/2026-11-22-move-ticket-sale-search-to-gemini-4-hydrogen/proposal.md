## Why

The published-sale searcher (TicketSale.SearchPublishedSales) still runs on `gemini-3.8-flash`, which is previous-generation and doubles in price on 2027-01-01 to that of `gemini-4-hydrogen`, so staying on it buys nothing after that date. Concert search already moved (`pass-tour-detail-pages-to-concert-search`), and showed that `gemini-4-hydrogen` at thinking `low` stops searching once the pages it has read look sufficient, so the switch needs its own evaluation before it ships.

## What Changes

- The ticket sale evaluation harness gets a fixture re-captured from current official pages (the current one is frozen at 2026-10-05 and its sales have since opened or left the pages), and records search queries, cost at the 2027-01-01 price, latency and empty responses per call.
- It compares `gemini-3.8-flash` and `gemini-4-hydrogen`, both at thinking `low`. If `gemini-4-hydrogen` misses sales that `gemini-3.8-flash` finds, a system instruction with a completion criterion (every sale the official pages announce for a series is in the answer) is evaluated on `gemini-4-hydrogen`.
- If `gemini-4-hydrogen` meets the acceptance criteria (design D3), the backend default (`defaultPublishedSaleSearchModel`) and the cloud-provisioning pin in the base `sales-phase-discovery` ConfigMap move to it together, with the prompt that passed. If it does not, both stay on `gemini-3.8-flash` and the tuning record says why.
- Concert search's labeled top-page links are not reused: sales are announced on ticket vendor pages, which that link list blocks by design.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none) — `components/entity/ticket-sale/search-published-sales` states what the search returns, independent of the model and prompt; this change keeps those requirements and their scenarios. The change sets `skip_specs: true`.

## Impact

- **backend:** `pkg/config` (`defaultPublishedSaleSearchModel`), `internal/infrastructure/gcp/gemini/ticket_sale_searcher.go` (system instruction, if a new one is adopted), `ticket_sale_eval_integration_test.go` (fixture and recorded columns), and the evaluation record in `docs/gemini-concert-searcher-tuning.md`.
- **cloud-provisioning:** `k8s/namespaces/backend/base/cronjob/sales-phase-discovery/configmap.env` (the model pin, which applies to dev and prod).
- **Cost:** 56 searches a month in prod (2026-10-21..11-20, 202 search queries); the evaluation is a few dozen calls.
- No proto, DB or spec change.
