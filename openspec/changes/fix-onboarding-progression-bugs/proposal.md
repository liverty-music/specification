## Why

The onboarding flow on dev has three bugs that together create a progression-blocking experience. After selecting a Home area, `ConcertService/ListWithProximity` returns 401 because the backend auth interceptor does not whitelist this public RPC. With no concert data, the lane introduction is skipped entirely, jumping the user straight to the My Artists spotlight. On the My Artists page, the coach mark's click-blocker covers the hype sliders that the user must interact with to complete onboarding — creating a deadlock where no tap can advance the flow. A secondary warning (`TicketJourneyRpcClient.listByUser is not a function`) indicates the deployed BSR package is stale.

## What Changes

- **Backend**: Add `ConcertService/ListWithProximity` to the auth interceptor's public-method whitelist so unauthenticated onboarding users can fetch concert data.
- **Frontend**: Fix the My Artists coach mark so the user can interact with hype sliders while the spotlight is active — either by providing an `onTap` dismissal callback, by opening a click-through window over the artist list area, or both.
- **Frontend**: Update the BSR package (`@buf/liverty-music_schema.connectrpc_es`) to resolve the `listByUser` runtime TypeError.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `concert-service`: `ListWithProximity` is specified as public but the backend auth interceptor blocks it — implementation must match the existing spec requirement.
- `onboarding-spotlight`: The click-blocker layer must allow interaction with elements below the spotlight target when the onboarding step expects sub-target interaction (hype sliders on My Artists).

## Impact

- **backend**: Auth interceptor configuration (public method whitelist) — no proto changes needed.
- **frontend**: Coach mark component CSS/logic for click-through on My Artists step; BSR dependency update in `package.json` / `package-lock.json`.
- **No breaking changes**. No spec-level requirement changes — the existing specs already describe the correct behavior; this change fixes implementation gaps.
