## Context

See proposal.md — Why. The detail sheet pushes `/concerts/:id` when it opens and, on a programmatic close (light dismiss, swipe, close control), calls `history.replaceState(null, '', '/dashboard')`. On browser back it only closes, since the browser has already navigated back. The dashboard writes its filter URL (`/dashboard?artists=…&journey=…&from=…`) from one `@watch` that runs as a queued task; on a deep-link the sheet opens in a task queued behind it (frontend#679), so the filtered URL is in place before the sheet pushes.

## Goals / Non-Goals

**Goals:**
- The URL after closing is exactly the dashboard URL before opening.

**Non-Goals:**
- Changing the sheet's push on open or the back-button behavior.
- Changing how the dashboard writes its filter URL.

## Decisions

### D1. Remember the URL at open, restore it on close

`open()` records `location.pathname + location.search` before it pushes `/concerts/:id`; `close()` restores that value with `replaceState` instead of the literal `/dashboard`. A deep-link records the filtered URL because the filter's URL write runs before the queued open.

- *Alternative — the sheet asks the dashboard to rebuild its filter URL on close*: couples the sheet to the dashboard's facets, and the sheet also opens from All Nearby, whose state is not in those facets. Rejected.
- *Alternative — `history.back()` on close*: pops the sheet's entry cleanly, but it is asynchronous and fires `popstate`. The router listens to `popstate` too and would navigate, which the spec forbids on close ("without triggering router navigation"). Rejected.

## Risks / Trade-offs

- [The recorded URL is stale if the dashboard rewrites its URL while the sheet is open] → The filter controls are behind the open sheet, and a filter change closes nothing, so the fan cannot change the facets mid-sheet. Accepted.
