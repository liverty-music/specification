## Context

See proposal.md - Why. `DiscoverForArtist` keeps a series whose last search is older than `salesPhaseSearchInterval` (`30 * 24 * time.Hour`), comparing `now.Sub(searchedTime)`. `searchedTime` is taken just before the search call, so it is a few seconds to a few minutes after 21:00 Japan time, depending on the artist's place in the run. The next run's `now` is taken when that artist's selection starts. Exactly N days later the elapsed time is therefore usually a little under N days, and the series waits one more day.

`pkg/config` still declares `GeminiSearchModelParse`, `GeminiSearchThinkingParse` and `GeminiSearchTemperature`, validates the first two thinking values, and resolves `SearchModelExtract()` and `SearchModelParse()`. Since tune-sales-phase-search no workload reads any of them: the concert searcher uses `ConcertSearchModel()` and `ConcertSearchThinkingLevel()`, and the sales-phase searcher uses `SalesPhaseSearchModel()` and `SalesPhaseSearchThinking()`. No ConfigMap in cloud-provisioning sets the three keys.

## Goals / Non-Goals

**Goals:**
- A series is searched again on the run 10 Japan-time dates after its last search.
- Remove the config that nothing reads.

**Non-Goals:**
- Making the interval configurable per environment.
- Changing the searcher, its prompt or its search window (change for the prompt's series id leak is separate).

## Decisions

**D1. Count calendar days in Japan time.** A series is due when `jstDate(now) - jstDate(searchedTime) >= 10` days, with `jstDate` truncating to the date in Asia/Tokyo. The job always runs at 21:00 Japan time, so this makes the interval exactly 10 daily runs regardless of where an artist falls in the run.

Alternative: keep `now.Sub(t) >= 10 * 24h` and subtract a margin (for example 1 hour). It hides the drift but still depends on run timing, and the margin is an arbitrary number.

**D2. Keep the interval a constant in the usecase.** `salesPhaseSearchInterval` becomes 10 days. The value is product behavior stated in the spec, so changing it goes through a change like this one rather than an environment variable that could make dev and prod differ from the spec.

Alternative: a `GCP_SALES_PHASE_SEARCH_INTERVAL` setting. It would allow tuning without a release, but the spec would then no longer state the interval.

**D3. Delete the unread config.** Remove the three fields, their validation, the two resolvers and `defaultSearchModelExtract` / `defaultSearchModelParse`, with their tests. An environment that still set one of the keys would be ignored by `envconfig`, which does not fail on unknown variables.

## Risks / Trade-offs

- [More searches per tracked series] → at most 3 a month for a series with nothing open, about 10 search queries each; the AI Studio spend cap remains the hard stop.
- [A series searched on day 0 and day 10 still misses a sale announced and opened in between] → accepted; a first-come sale opening within the interval is the same gap as before, only shorter.

## Migration Plan

1. backend PR with the interval, the date counting and the config removal; release.
2. `bump-prod-pin` pins the release; no ConfigMap or migration change. Series already searched are due 10 Japan-time dates after their recorded search.

Rollback: revert the image pin.
