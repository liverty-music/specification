## Why

Sales-phase discovery searches a tracked series again only 30 days after its last search. Sales are usually announced a few days to two weeks before they open, so a sale the first search missed, or one announced right after it, is often found too late. In the first prod run on 2026-10-06 the YOASOBI search pointed at an upcoming playguide presale but returned nothing, and that series will not be searched again for 30 days. The search is now cheap: 51 search queries for 5 artists, mostly within the free tier, and at most about ¥2.2 per paid query. Separately, three Gemini search settings are no longer read by any workload since tune-sales-phase-search.

## What Changes

- Discovery searches a series again when its last search was 10 or more days ago, instead of 30.
- The interval counts calendar days in Japan time: a series searched on 7 October is searched again from the 17 October run. The daily run starts at 21:00 Japan time and records each search a little after the previous run's time, so measuring elapsed time made the interval one day longer than stated.
- The backend no longer reads `GCP_GEMINI_SEARCH_MODEL_PARSE`, `GCP_GEMINI_SEARCH_THINKING_PARSE` and `GCP_GEMINI_SEARCH_TEMPERATURE`, and the unused config resolvers `SearchModelExtract()` and `SearchModelParse()` are deleted. No ConfigMap sets these keys.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/usecase/sales-phase/discover-for-artist`: the search interval in "Only series that need a search are searched" becomes 10 calendar days in Japan time, and "A successful search is recorded" says 10 days.

Unchanged: `components/entity/sales-phase-search-log` and its `list-by-series` and `record` operations store and return the searched time without interpreting it, and `components/entity/sales-phase/get-by-series` and `components/entity/ticket-journey/list-user-ids-tracking-series` are read as before.

## Impact

- backend:
  - `internal/usecase/sales_phase_uc.go`: the interval constant and its comparison
  - `internal/usecase/sales_phase_uc_test.go`: the interval scenarios
  - `pkg/config/config.go` and its tests: the three unread settings and two resolvers removed
- Search cost: a tracked series with nothing open is searched at most about 3 times a month instead of once, about 10 search queries each.
- No migration, no proto change, no ConfigMap change.
