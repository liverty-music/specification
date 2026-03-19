## Why

The onboarding tutorial's Step 1 → Dashboard transition gate is broken. The spec requires "concert search results have been received for all followed artists" before activating the Dashboard coach mark, but `SearchNewConcerts` is a fire-and-forget RPC that returns immediately while the actual Gemini search runs in a background goroutine (up to 120s). The frontend treats RPC completion as "search done" and immediately queries `ListWithProximity`, which returns empty because the backend hasn't finished searching or writing concerts to the DB yet. As a result, `concertGroupCount` is always 0 and the spotlight/coach mark never appears.

## What Changes

- Clarify the definition of "concert search completion" in the onboarding tutorial spec: completion means the backend search log has reached `COMPLETED` or `FAILED` status, not that the `SearchNewConcerts` RPC call returned.
- Frontend `ConcertSearchTracker` SHALL poll `ListSearchStatuses` to detect actual backend search completion, instead of using RPC return as a signal.
- The existing 15-second per-artist timeout is retained as the polling deadline (fallback for slow or stuck searches).
- `verifyConcertData()` SHALL only be called after all followed artists have reached a terminal search state via polling.
- Add the `ListSearchStatuses` polling requirement to the `concert-search-log` spec for onboarding use cases.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `onboarding-tutorial`: Redefine "concert search results have been received" to mean backend search log status is `COMPLETED` or `FAILED` (verified via `ListSearchStatuses` polling), not `SearchNewConcerts` RPC return.
- `concert-search-log`: Add requirement for frontend polling pattern during onboarding — poll `ListSearchStatuses` every 2s per artist with a 15s deadline.

## Impact

- **Frontend**: `ConcertSearchTracker` in `frontend/src/routes/discovery/concert-search-tracker.ts` — replace fire-and-forget flow with polling loop.
- **Frontend**: `ConcertService` in `frontend/src/services/concert-service.ts` — already exposes `listSearchStatuses()`, no changes needed.
- **Backend**: No changes — `ListSearchStatuses` RPC and search log infrastructure already exist and work correctly.
- **Specification**: Two existing capability specs updated with clarified requirements.
