## Context

The onboarding flow progresses: Discovery (Step 1) → Dashboard (Step 3) → My Artists (Step 5) → Signup (Step 6). The transition from Step 1 to Step 3 is gated by `showDashboardCoachMark`, which currently requires only that `SearchNewConcerts` RPC calls have completed (or timed out). It does not verify that `ConcertService/List` will return any data.

When the Dashboard loads with zero concert groups, the live-highway component renders its empty state (`if.bind="!loading && isEmpty"`), so the lane header elements (`[data-stage-home]`, etc.) and concert card elements (`[data-live-card]`) are absent from the DOM. The coach mark's `findAndHighlight()` retries for 5 seconds, then only sets `visible = false` without closing the popover or releasing the scroll lock, leaving the UI inoperable.

Three layers need fixing: (1) the Discovery gate, (2) the Dashboard fallback, (3) the coach mark cleanup.

## Goals / Non-Goals

**Goals:**
- Prevent the Dashboard coach mark from activating when no concerts exist for the followed artists
- Provide user feedback when concert searches complete with no results
- Gracefully handle the edge case where the user reaches the Dashboard during onboarding with zero data (defense-in-depth)
- Ensure the coach mark component never leaves orphaned overlays

**Non-Goals:**
- Changing the backend `ConcertService/List` or `SearchNewConcerts` APIs
- Adding retry logic for concert searches (already has 15s timeout per artist)
- Modifying the non-onboarding Dashboard behavior

## Decisions

### Decision 1: Pre-check via `ConcertService/List` on Discovery page

**Chosen**: After all `SearchNewConcerts` calls complete, call `ConcertService/List` to verify at least 1 date group exists before activating the Dashboard coach mark.

**Why**: This is the earliest point to detect the empty-data scenario. The existing `completedSearchCount` tracking already knows when all searches are done — adding a List call at that point is minimal overhead.

**Alternative considered**: Check individual `SearchNewConcerts` responses for result counts. Rejected because `SearchNewConcerts` is a fire-and-forget background job — it doesn't return concert counts in its response.

### Decision 2: Guidance message for zero-concert state

**Chosen**: When all concert searches complete but `ConcertService/List` returns empty, update the guidance HUD message to prompt the user to follow more artists ("No upcoming events found. Try following more artists!"). Do not show the Dashboard coach mark.

**Why**: The user needs feedback to understand why the coach mark hasn't appeared. Without guidance, they would be stuck on the Discovery page with no clear next action.

### Decision 3: Dashboard fallback — skip lane intro to My Artists

**Chosen**: If `startLaneIntro()` runs with `dateGroups.length === 0`, skip the entire lane intro and advance directly to Step 4 (My Artists tab spotlight).

**Why**: Defense-in-depth. The user could reach the Dashboard via direct nav tap (bypassing the coach mark gate). Rather than showing a broken lane intro, gracefully skip to the next meaningful step.

### Decision 4: Coach mark `deactivate()` on retry exhaustion

**Chosen**: Replace `this.visible = false` with `this.deactivate()` in `findAndHighlight()` when retries are exhausted.

**Why**: `deactivate()` properly closes the popover, releases the scroll lock, clears the anchor-name, and stops retry timers. The partial cleanup was the direct cause of the stuck overlay.

## Risks / Trade-offs

- **[Risk] `ConcertService/List` adds a network call to Discovery** → Mitigation: This call is only made once after all searches complete. The Dashboard will make the same call anyway, so the data is useful regardless.
- **[Risk] User could be stuck on Discovery if no artists have concerts** → Mitigation: The guidance message tells them to follow more artists. The underlying data issue (no concerts for followed artists) is expected for niche/new artists.
- **[Trade-off] Dashboard fallback skips the lane intro entirely** → Accepted: An empty Dashboard has no lanes to introduce. The lane intro can be experienced on subsequent visits once concerts are available.
