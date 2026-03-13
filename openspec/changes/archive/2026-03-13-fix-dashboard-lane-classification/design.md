## Context

The dashboard timeline classifies concerts into three proximity lanes (Home / Near / Away) based on the user's home area. Two implementation bugs cause all concerts to display in "Away Stage":

1. During onboarding, `loadData()` fires before the user selects a home. After selection, `onHomeSelected()` does not reload data, so the stale all-Away result persists.
2. After sign-up, `needsRegion` checks `localStorage('guest.home')` which was already cleared by `GuestDataMergeService.clearAll()`. The backend has the user's home (set atomically via `CreateRequest.home`), but the dashboard never queries it.

The `user-home` spec already defines the correct behavior: authenticated users SHALL read home from `UserService.Get`, guests SHALL fall back to localStorage. The `UserHomeSelector.confirmSelection()` method already distinguishes authenticated vs guest for writes (RPC vs localStorage), but `getStoredHome()` only reads localStorage.

## Goals / Non-Goals

**Goals:**
- Fix lane classification during onboarding so concerts are re-classified after home selection
- Align `needsRegion` determination with `user-home` spec: authenticated users check backend, guests check localStorage
- Keep changes minimal and contained to the dashboard and home selector

**Non-Goals:**
- Changing the backend `ListByFollowerGrouped` classification logic (it works correctly given a home)
- Modifying the `GuestDataMergeService.clearAll()` behavior (clearing `guest.*` is correct by design)
- Adding new RPC endpoints or proto changes

## Decisions

### D1: Reload data after home selection during onboarding

**Chosen**: Add `this.loadData()` in `dashboard.ts:onHomeSelected()` after storing the home. During onboarding (guest phase), the backend still receives `home=nil` because the guest home is only in localStorage. However, once data reload is in place, the correct classification will work after sign-up when the backend has the home.

**Consideration**: During the guest onboarding phase, the backend has no home for this user, so a reload would still return all-Away. The real fix requires combining D1 with D2 — after sign-up, the dashboard loads with the backend-known home and correctly classifies lanes. For the initial guest dashboard visit, the lane intro plays over the correctly-classified data only if the backend knows the home, which it doesn't yet during guest phase.

**Revised approach**: The `onHomeSelected()` reload alone doesn't help during guest phase because the backend doesn't know the guest's home. The meaningful fix is ensuring the post-sign-up dashboard visit works correctly (D2). However, adding the reload is still correct for the Settings page scenario where an authenticated user changes their home.

### D2: Use backend User.home for authenticated users' `needsRegion` check

**Chosen**: Modify the dashboard's `loading()` lifecycle to fetch the user's home status from the backend when authenticated, instead of relying on `localStorage('guest.home')`.

**Approach**: The dashboard already calls `dashboardService.loadDashboardEvents()` which calls `concertService.listByFollower()`. The `ListByFollowerGrouped` RPC already uses the backend home for classification. The issue is only the `needsRegion` UI flag.

Two options:

**Option A — Fetch User via UserService.Get**: Call `UserService.Get` in `loading()` to check `user.home`. This adds one RPC call but gives a definitive answer.

**Option B — Infer from loadData result**: After `loadData()` resolves, check if any concerts landed in `home` or `nearby` lanes. If yes, the backend has a home set. If all are in `away`, the home might be missing — but this is ambiguous (all concerts could legitimately be far away).

**Decision**: Option A. An explicit `UserService.Get` check is unambiguous and aligns with the spec requirement. The RPC is lightweight and can be parallelized with `loadDashboardEvents()`.

**Implementation**: In `dashboard.ts:loading()`:
- If authenticated: fetch `UserService.Get` → check `user.home` → set `needsRegion`
- If guest: fall back to `UserHomeSelector.getStoredHome()` (current behavior)

### D3: Keep `getStoredHome()` as guest-only utility

**Chosen**: Do not modify `UserHomeSelector.getStoredHome()` to also query the backend. It remains a synchronous localStorage check, used only for guests. The dashboard takes responsibility for choosing the right source based on auth state.

**Rationale**: Making `getStoredHome()` async (to support an RPC call) would change the call sites and add complexity. The dashboard is the only consumer that needs the authenticated path, so localizing the logic there is simpler.

## Risks / Trade-offs

- **[Extra RPC call on dashboard load]** → `UserService.Get` adds one request for authenticated users. Mitigation: parallelize with `loadDashboardEvents()` using `Promise.all`. The call is lightweight (single row lookup).
- **[Guest onboarding lane intro still shows all-Away]** → During the guest phase, the backend has no home, so lanes cannot be classified. Mitigation: This is inherent to the guest model — lane classification requires a server-side home. The lane intro labels (HOME / NEAR / AWAY) still explain the concept even with empty home/near columns. The correct classification appears after sign-up when the user returns to the dashboard.
