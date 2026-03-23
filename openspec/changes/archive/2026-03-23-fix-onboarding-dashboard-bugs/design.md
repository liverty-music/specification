## Context

Three bugs are occurring simultaneously at the dashboard step of the onboarding flow. All can be resolved with frontend-only changes. No backend API or infrastructure changes are needed.

Current state:
- When a guest user reaches the dashboard, the auth-required `ListByUser` RPC is called, producing a 401 error in the console
- `scrollTo({ top: scrollHeight })` is called synchronously after `showPopover()`, but since the top-layer layout has not completed, the scroll has no effect and the dismiss-zone (at the top of the screen) is visible
- When `router.load()` is called during an active spotlight, the View Transition API crashes with invalid state

## Goals / Non-Goals

**Goals:**
- Eliminate unnecessary RPC calls and 401 errors for guest users
- Ensure bottom-sheet operates per spec ("swipe down to dismiss") with sheet-body visible on initial display
- Prevent errors during route transitions while coach marks are active
- Unify RPC client initialization patterns

**Non-Goals:**
- Full refactoring of the coach mark system (this change only fixes the transition error)
- Design changes or animation additions for bottom-sheet
- Backend-side authentication logic changes

## Decisions

### D1: Add auth guard to fetchJourneyMap

**Choice**: Check `IAuthService.isAuthenticated` inside `DashboardService.fetchJourneyMap()` and return an empty Map immediately when unauthenticated, without calling the RPC.

**Alternatives**:
- A) Guard inside TicketJourneyRpcClient → Not the service layer's responsibility. Would affect other callers
- B) Guard in dashboard-route.ts loading() → Callers would need to know DashboardService internals

**Rationale**: fetchJourneyMap already has a fallback of "return empty Map when no journey data." The auth check is a natural extension of this, belonging in the same place.

### D2: Unify TicketJourneyRpcClient to constructor pattern

**Choice**: Move field initialization into the constructor, matching the FollowRpcClient pattern. Also unify from `createClient` (new API) to `createPromiseClient` (existing pattern).

**Rationale**: Codebase consistency. No functional difference, but improves reviewability and maintainability.

### D3: Defer scrollTo by one frame with requestAnimationFrame

**Choice**: Defer `scrollTo({ top: scrollHeight })` after `showPopover()` by one frame using `requestAnimationFrame`. Do not change DOM order, scroll-snap-align, onScrollEnd logic, or backdrop-fade.

**Alternatives**:
- A) Reverse DOM order (move dismiss-zone below) → sheet-body sticks to the top of the screen. `margin-block-start: auto` does not work in scroll containers without free space. Fundamentally incompatible with the bottom-sheet UX pattern
- B) Use CSS Anchor Positioning → Inappropriate for the bottom-sheet use case

**Rationale**: In the bottom-sheet UX pattern, the dismiss-zone is placed at the top (near scrollTop=0) and the sheet-body at the bottom. "Swipe down to dismiss" refers to the physical gesture direction, corresponding to decreasing scrollTop (scrolling toward the top). The original DOM order is correct; the only problem was that `scrollTo()` was called synchronously before `showPopover()` completed its top-layer layout. Waiting one frame with `requestAnimationFrame` ensures the scroll takes effect after layout completion.

### D4: Clean up spotlight in detaching()

**Choice**: Add `this.onboarding.deactivateSpotlight()` to `dashboard-route.ts`'s `detaching()`.

**Alternatives**:
- A) Clean up in `unloading()` (router lifecycle) → Executes before `detaching()` in the navigation sequence, so it could cancel the View Transition earlier, but existing cleanup code (AbortController, timers, scroll listeners) is consolidated in `detaching()`, so it would break consistency

**Rationale**: Cleaning up resources in Aurelia lifecycle hooks is the correct pattern. Existing cleanup is consolidated in `detaching()`, which executes reliably regardless of the navigation trigger (coach mark, nav tab, browser back).

### D5: Replace router.load() with declarative navigation

**Choice**: Remove `router.load('my-artists')` from `onOnboardingMyArtistsTapped()` and keep only state updates (`setStep`). Navigation is delegated to the existing `currentTarget.click()` → Aurelia Router `useHref` intercept.

**Mechanism**: The coach-mark's `target-interceptor` div receives the user's click and calls `currentTarget.click()` in `onTargetClick()`. When the target is `<a href="my-artists">`, this programmatic `.click()` triggers Aurelia Router's `useHref` intercept, performing the route transition declaratively. The `onTap` callback handles only state updates.

**Note**: `e.preventDefault()` on the `target-interceptor` div is effectively a no-op since divs have no default action. `e.stopPropagation()` only stops event propagation from the interceptor div and does not affect events fired on the target element via `currentTarget.click()`. Therefore, no changes to `preventDefault` / `stopPropagation` are needed.

**Alternatives**:
- A) Call `deactivateSpotlight()` then `router.load()` → Works but leaves imperative navigation in place
- B) Call `skipTransition()` on the View Transition before navigating → Complex and fragile

**Rationale**: Leveraging Aurelia Router's declarative navigation (`useHref` intercept) eliminates imperative `router.load()` and avoids View Transition collisions.

## Risks / Trade-offs

- **[D3] requestAnimationFrame reliability** → Whether one frame delay is sufficient depends on browser implementation. Visual verification on major browsers (Chrome, Safari, Firefox) is required. If it doesn't work, a double-rAF (rAF inside rAF) fallback for a two-frame wait should be considered.
- **[D5] `currentTarget.click()` and Aurelia Router `useHref` intercept compatibility** → Whether programmatic `.click()` correctly fires the `useHref` intercept needs verification. Aurelia Router does not check the `isTrusted` property of click events (as of 2025 implementation), so it should work, but behavior may change in future Aurelia updates.
- **[D1] Position of isAuthenticated check** → Adds an IAuthService dependency to DashboardService. Since it already indirectly references auth state via IGuestService, there is no new dependency direction issue.
