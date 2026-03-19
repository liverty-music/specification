## Context

The onboarding Discovery → Dashboard transition is gated by `showDashboardCoachMark`, which requires `allSearchesComplete && concertGroupCount > 0`. The `ConcertSearchTracker` fires `SearchNewConcerts` RPC per artist and calls `markSearchDone()` when the RPC promise resolves. However, `SearchNewConcerts` is implemented as `AsyncSearchNewConcerts` on the backend — it spawns a background goroutine and returns immediately. The actual Gemini search, event publishing, and DB persistence happen asynchronously (up to 120s).

This means `markSearchDone()` fires within milliseconds of the RPC call, long before concerts exist in the database. The subsequent `verifyConcertData()` → `listWithProximity()` call always returns empty groups, so the coach mark never activates.

The backend already provides `ListSearchStatuses` RPC that returns the actual search log state (`PENDING`, `COMPLETED`, `FAILED`) per artist. The frontend has this method wired up but unused in `ConcertSearchTracker`.

## Goals / Non-Goals

**Goals:**
- Fix the concert data gate so the Dashboard coach mark activates when concerts actually exist in the DB
- Use `ListSearchStatuses` polling to detect real backend search completion
- Preserve the 15-second per-artist timeout as the polling deadline (UX guarantee)
- Keep the fix entirely in the frontend — no backend API changes needed

**Non-Goals:**
- Adding WebSocket or server-sent events for push-based search status updates
- Changing the `SearchNewConcerts` RPC to be synchronous
- Modifying the Watermill event pipeline or concert persistence flow
- Changing polling behavior for non-onboarding (authenticated) flows

## Decisions

### D1: Poll `ListSearchStatuses` instead of relying on RPC return

**Chosen**: After firing each `SearchNewConcerts` RPC, start a polling loop that calls `ListSearchStatuses` every 2 seconds. An artist's search is considered "done" when its status is `COMPLETED` or `FAILED`, or when the 15-second per-artist timeout elapses.

**Why**: The backend search log already tracks the exact lifecycle (`PENDING` → `COMPLETED`/`FAILED`). Polling this is the simplest approach that requires zero backend changes. The `ListSearchStatuses` RPC accepts multiple artist IDs in a single call, so we can batch all pending artists into one poll request.

**Alternative considered**: Wait for `SearchNewConcerts` to become synchronous. Rejected because the async design is intentional — the Gemini API call takes 5-30 seconds, and blocking the RPC would make the UI feel unresponsive. The fire-and-forget + poll pattern is the correct architecture.

**Alternative considered**: Use individual per-artist polling. Rejected in favor of batched polling — one `ListSearchStatuses` call with all pending artist IDs is more efficient than N individual calls.

### D2: Batched polling with a single interval timer

**Chosen**: Use a single `setInterval(2000)` timer that polls `ListSearchStatuses` for all artists whose status is still `PENDING`. When an artist reaches `COMPLETED`/`FAILED`, mark it done. When all artists are done (or timed out), clear the interval and call `verifyConcertData()`.

**Why**: A single timer is simpler to manage than per-artist timers. The batch call is cheap (one RPC regardless of artist count). The 2-second interval balances responsiveness with network overhead — searches typically complete in 5-15 seconds.

**Alternative considered**: Exponential backoff polling. Rejected because the search window is short (15s) and a fixed 2s interval only results in ~7 polls max. The added complexity of backoff isn't justified.

### D3: Retain 15-second timeout as polling deadline, not RPC timeout

**Chosen**: The existing `setTimeout(15_000)` per artist remains, but its role changes from "RPC timeout" to "polling deadline." If an artist's status hasn't reached `COMPLETED`/`FAILED` after 15 seconds, it's treated as done (with the assumption that the search is either stuck or slow, and `verifyConcertData()` will check actual data availability regardless).

**Why**: The 15-second timeout is a UX guarantee — users should not wait indefinitely on the Discovery page. If the backend search takes longer than 15s, the user can still proceed; the concert data may appear on subsequent dashboard visits once the background search completes.

### D4: `verifyConcertData()` unchanged

**Chosen**: Keep `verifyConcertData()` as-is — it calls `listWithProximity()` and sets `concertGroupCount`. The only change is *when* it's called (after polling confirms completion, not after RPC return).

**Why**: The verification logic is correct. The bug is purely about timing — `verifyConcertData()` was called too early, not that it checked the wrong thing.

## Risks / Trade-offs

- **[Risk] `ListSearchStatuses` adds network overhead during onboarding** → Mitigation: One batched RPC call every 2 seconds for ~7 iterations max (15s ÷ 2s). Total additional RPCs: ~7 per onboarding session. Negligible.

- **[Risk] Backend search completes but event subscriber hasn't written to DB yet** → Mitigation: The search log transitions to `COMPLETED` after `executeSearch()` finishes, which includes publishing the `concert.discovered.v1` event. There is a small window between event publish and subscriber DB write where `ListWithProximity` could return empty. However, the Watermill subscriber processes events near-instantly (in-process, not cross-service). If this window proves problematic, a 1-second delay between polling completion and `verifyConcertData()` could be added, but this is unlikely to be needed.

- **[Risk] Search log stays `PENDING` indefinitely (crashed goroutine)** → Mitigation: The 15-second frontend timeout acts as a circuit breaker. Additionally, the backend's `ListSearchStatuses` already treats entries pending for >3 minutes as `FAILED` (self-healing).

- **[Trade-off] 2-second poll interval means up to 2s delay after search completion** → Accepted: Users are browsing bubbles during this time. A 2-second delay is imperceptible in the context of an interactive discovery experience.
