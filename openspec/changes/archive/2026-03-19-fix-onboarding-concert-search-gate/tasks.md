## 1. Refactor ConcertSearchTracker to use polling

- [x] 1.1 Add `ConcertSearchClient.listSearchStatuses(artistIds, signal)` to the tracker's client interface (`ConcertSearchClient` in `concert-search-tracker.ts`)
- [x] 1.2 Replace `searchConcertsWithTimeout` logic: fire `searchNewConcerts` RPC (fire-and-forget, ignore promise resolution for marking done), record the artist ID and start time in a pending set
- [x] 1.3 Implement batched polling loop: `setInterval(2000)` that calls `listSearchStatuses` with all pending artist IDs, marks artists done when status is `COMPLETED` or `FAILED`
- [x] 1.4 Implement per-artist 15-second timeout: if an artist has been pending for ≥15s, treat it as done regardless of poll result
- [x] 1.5 When all artists are done and `allSearchesComplete` is true, clear the polling interval and call `verifyConcertData()`
- [x] 1.6 Add polling error handling: log errors, skip marking artists done, let the next poll cycle retry
- [x] 1.7 Update `dispose()` to clear the polling interval timer in addition to existing timeout cleanup

## 2. Update tests

- [x] 2.1 Update `concert-search-tracker.spec.ts` unit tests to verify polling behavior: mock `listSearchStatuses` to return `COMPLETED` and verify `verifyConcertData` is called after polling, not after RPC return
- [x] 2.2 Add test: polling timeout — mock `listSearchStatuses` to always return `PENDING`, verify artist is marked done after 15s
- [x] 2.3 Add test: polling error resilience — mock `listSearchStatuses` to throw, verify retry on next cycle and timeout still applies
- [x] 2.4 Add test: batched polling — follow 3 artists, verify single `listSearchStatuses` call with all 3 IDs
- [x] 2.5 Verify existing `showDashboardCoachMark` tests pass with the new polling flow
