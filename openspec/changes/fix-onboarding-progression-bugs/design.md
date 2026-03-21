## Context

The onboarding flow on dev (`dev.liverty-music.app`) has three bugs discovered during manual testing:

1. `ConcertService/ListWithProximity` returns 401 for guest users because it is missing from the backend auth interceptor's public method whitelist — despite the concert-service spec explicitly stating it does not require authentication.
2. On the My Artists page, the coach mark's click-blocker layer covers the hype sliders, making it impossible for the user to interact with them and complete onboarding. The `activateSpotlight` call omits the `onTap` callback.
3. The deployed BSR package (`@buf/liverty-music_schema.connectrpc_es`) is stale — `TicketJourneyService.listByUser` exists in the proto definition but is missing at runtime, causing a `TypeError`.

Current auth whitelist in `backend/internal/di/provider.go`:
```
ArtistService/ListTop, ListSimilar, Search
ConcertService/List, SearchNewConcerts, ListSearchStatuses
```
`ConcertService/ListWithProximity` is absent.

## Goals / Non-Goals

**Goals:**
- Guest onboarding users can fetch proximity-grouped concerts without authentication
- My Artists onboarding step allows hype slider interaction to complete the flow
- BSR package is up-to-date so `TicketJourneyRpcClient.listByUser` works at runtime

**Non-Goals:**
- Changing the coach mark component's general architecture
- Adding new onboarding steps or modifying the step order
- Fixing the lane introduction UX when concert data is legitimately empty

## Decisions

### D1: Add `ListWithProximity` to public procedures whitelist

Add one entry to the `publicProcedures` map in `backend/internal/di/provider.go`:

```go
"/" + concertconnect.ConcertServiceName + "/ListWithProximity": true,
```

**Why**: The spec already defines this as a public RPC. The handler comment says "Authentication is not required." This is a missing configuration, not a design gap.

**Alternative considered**: Making the frontend pass a guest token or service account credential during onboarding. Rejected — adds unnecessary complexity when the RPC is designed to be public.

### D2: Dismiss coach mark on tap, then let user interact with sliders

On the My Artists onboarding step, provide an `onTap` callback to `activateSpotlight` that deactivates the spotlight. This reveals the hype sliders underneath, which the user can then interact with to complete onboarding via the existing `onHypeChanged` handler.

```
Step 5: My Artists
┌────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐
│ Coach mark active       │     │ Sliders accessible      │     │ Onboarding complete     │
│ [data-hype-header] lit  │────▶│ User adjusts hype       │────▶│ deactivateSpotlight()  │
│ "熱量を上げておこう"     │ tap │ onHypeChanged fires     │     │ setStep(COMPLETED)      │
└────────────────────────┘     └────────────────────────┘     └────────────────────────┘
```

In `my-artists-route.ts`, change from:
```typescript
this.onboarding.activateSpotlight(
  '[data-hype-header]',
  '絶対に見逃したくないアーティストの熱量を上げておこう',
)
```
To:
```typescript
this.onboarding.activateSpotlight(
  '[data-hype-header]',
  '絶対に見逃したくないアーティストの熱量を上げておこう',
  () => this.onboarding.deactivateSpotlight(),
)
```

**Why**: Minimal change. Reuses the existing `onTap` callback mechanism and `deactivateSpotlight()`. The user taps the spotlight target (hype header) → spotlight dismisses → sliders become interactive → hype change completes onboarding.

**Alternative considered**: Modifying `onBlockerClick()` to support a dismissal callback so tapping anywhere outside the target also dismisses. This would require changing the coach-mark component API. Could be a follow-up improvement but is not needed to unblock the flow — tapping the highlighted target is the natural action.

### D3: Update BSR package via `npm install`

Run `npm install` in the frontend to pull the latest BSR package version that includes the `TicketJourneyService.listByUser` RPC. Then redeploy.

**Why**: The lock file references commit `72ea9d75f704` (March 19) but the installed version is `019227fea01d` (March 18). A fresh install resolves to the latest version matching the semver range in `package.json`.

## Risks / Trade-offs

- **[Risk] Coach mark tap target may be small on mobile** → The `[data-hype-header]` element is a sticky header spanning full width, so it should be easy to tap. If users still struggle, a follow-up can add `onBlockerClick` dismissal.
- **[Risk] BSR package version drift** → After `npm install`, the lock file will update. CI must rebuild with the new lock file. Low risk since this is a dev environment fix.
- **[Risk] Other public RPCs may also be missing from whitelist** → Out of scope for this change, but worth auditing. The `ListWithProximity` omission was introduced when the RPC was added in a recent PR.

## Open Questions

(none — all decisions are straightforward implementation fixes)
