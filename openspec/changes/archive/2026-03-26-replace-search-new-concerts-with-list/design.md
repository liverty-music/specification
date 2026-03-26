## Context

The Discovery page (`discovery-route.ts`) calls `searchConcertsForArtist()` after every follow action and on page load (for pre-seeded guest follows). This method internally calls `SearchNewConcerts` RPC before calling `List` to check for concerts.

`SearchNewConcerts` is intended as a data-ingestion operation (AI-powered external search, up to 60 seconds). It is correctly triggered by:
1. The daily `concert-discovery` CronJob
2. The backend `followUseCase.triggerFirstFollowSearch()` on first follow (already checks search log to avoid redundant calls)

The frontend calling it directly is redundant with (2) and incorrect in all other cases.

The UX value of `searchConcertsForArtist` is:
- Show a snack notification if the artist has upcoming concerts
- Increment `artistsWithConcerts` to advance the onboarding coach mark

Both of these can be satisfied by calling `ConcertService.List` alone.

## Goals / Non-Goals

**Goals:**
- Remove all `SearchNewConcerts` calls from the frontend
- Preserve the snack notification and onboarding coach mark behavior
- Keep `searchConcertsForArtist` logic intact (just remove the `searchNewConcerts` call inside it)
- Remove the now-unused `searchNewConcerts` method from `ConcertServiceClient`

**Non-Goals:**
- Polling for newly discovered concerts after follow (out of scope for this change)
- Changes to the backend `SearchNewConcerts` handler or `follow_uc.go`
- Changes to the `SearchNewConcerts` proto definition
- Real-time snack notification when the backend's async search completes

## Decisions

### Decision: Keep `searchConcertsForArtist`, remove only the `searchNewConcerts` call inside it

**Rationale:** The method's remaining logic (call `List` → update `artistsWithConcerts` → show snack) is still needed. Removing the method entirely would require duplicating that logic at each call site. Keeping the method and removing the `searchNewConcerts` line is the minimal, correct change.

**Alternative considered:** Rename method to `fetchConcertsForArtist` to reflect its new role.
**Decision:** Keep the name as-is to minimize diff size. Rename can be done as a follow-up if desired.

### Decision: No change to `loading()` call pattern

`loading()` calls `searchConcertsForArtist` for each pre-seeded guest follow. After this change, it will call `List` for each artist instead of `SearchNewConcerts` + `List`. This is correct: at page load, we only want to read what's already in the DB. The backend's first-follow trigger has already run (or will run) independently.

### Decision: Remove `searchNewConcerts` from `ConcertServiceClient`

After this change, the method has no callers in the frontend. Removing it prevents accidental re-use and clarifies the frontend's contract: the frontend is a consumer of concert data, not a trigger for concert discovery.

## Risks / Trade-offs

**[Risk] Snack notification may not fire for newly followed artists**
After following an artist, the backend's `triggerFirstFollowSearch` runs asynchronously. If `List` is called before the search completes, it will return empty and no snack is shown.
→ Mitigation: Accepted trade-off for this change. The snack was already unreliable (race condition existed before). Polling is the correct fix and is tracked separately.

**[Risk] `loading()` no longer triggers search for pre-seeded guest follows**
Guest follows that were seeded before the Discovery page loaded will no longer trigger `SearchNewConcerts` at page load.
→ Mitigation: The CronJob runs daily and will pick up these artists. The first-follow backend trigger already fired when the artist was originally followed. Acceptable.
