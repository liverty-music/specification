## Why

Three bugs are occurring simultaneously at the dashboard step of the onboarding flow, blocking the guest user's first experience. A 401 error appears in the console, the home area selection sheet renders at the top of the screen, and a route transition error crashes during coach mark interaction. All are regressions discovered during onboarding refinement work and require immediate fixes.

## What Changes

- **Bug 1: ListByUser 401 Error** — `DashboardService.fetchJourneyMap()` calls the `TicketJourneyService.ListByUser` RPC even for guest (unauthenticated) users. Add an auth guard to skip the RPC and return an empty Map when unauthenticated. Also unify `TicketJourneyRpcClient` initialization pattern with `FollowRpcClient`.
- **Bug 2: Bottom Sheet Display Timing** — The `bottom-sheet` component calls `scrollTo()` synchronously after `showPopover()`, but the top-layer layout has not completed yet, so the scroll has no effect and the dismiss-zone (at the top) is visible. Defer the scroll by one animation frame.
- **Bug 3: Coach Mark View Transition Error** — The spotlight is not cleaned up in dashboard's `detaching()`, causing a View Transition collision during route transition. Ensure cleanup in the lifecycle hook and replace imperative `router.load()` with declarative navigation.

## Capabilities

### New Capabilities

(None — bug fixes for existing features only)

### Modified Capabilities

- `bottom-sheet-ce`: Defer `scrollTo()` by one animation frame after `showPopover()` to ensure top-layer layout completion
- `onboarding-spotlight`: Add spotlight cleanup on route detach and View Transition safety requirements

## Impact

- **Frontend only** — No backend or infrastructure changes
- Affected components:
  - `src/services/dashboard-service.ts` — Auth guard added
  - `src/adapter/rpc/client/ticket-journey-client.ts` — Initialization pattern change
  - `src/components/bottom-sheet/` — HTML/CSS/TS all changed
  - `src/routes/dashboard/dashboard-route.ts` — detaching cleanup, router.load removal
  - `src/components/coach-mark/coach-mark.ts` — preventDefault review
