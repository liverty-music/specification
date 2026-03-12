## Context

During onboarding, unauthenticated guest users follow artists on the `/discover` page. The `FollowServiceClient` branches on `onboarding.isOnboarding`: when `true`, follows are saved to localStorage; when `false`, they go to the backend RPC (which requires authentication).

Currently, `/discover` is configured with `data: { auth: false }` but no `tutorialStep`. The `AuthHook.canLoad()` short-circuits on `auth === false` (line 37) and returns `true` immediately — it never reaches the tutorial step logic. As a result, the onboarding step is never validated or enforced for this route, and `isOnboarding` returns `false` when `onboardingStep` is 0 (LP) or unset.

The `onboarding/loading` route has the same issue: `data: { auth: false, tutorialStep: 2 }` — the `tutorialStep` is dead because the `auth: false` check fires first.

### Normal flow (works)

```
Welcome Page → "Get Started" → setStep(DISCOVER=1) → navigate(/discover)
→ isOnboarding=true → localStorage follow ✓
```

### Broken flow (direct access)

```
Direct access to /discover (or localStorage cleared)
→ onboardingStep=0 → isOnboarding=false → RPC follow → 401 ✗
```

## Goals / Non-Goals

**Goals:**
- Guest users on `/discover` during onboarding SHALL always use localStorage follow (never hit backend RPC)
- The auth hook SHALL enforce `tutorialStep` even on routes marked `auth: false`
- Direct URL access to `/discover` without an active onboarding session SHALL redirect to the landing page

**Non-Goals:**
- Changing the route path from `/discover` to `/onboarding/discover` (keep current path, update spec instead)
- Changing `FollowServiceClient` branching logic (it is correct; the problem is upstream)
- Adding server-side onboarding state

## Decisions

### 1. Refactor auth hook to check tutorialStep before short-circuiting on auth: false

**Decision**: Change `AuthHook.canLoad()` so that routes with both `auth: false` and `tutorialStep` are processed through the tutorial logic, not short-circuited.

**Current behavior** (line 37-39):
```typescript
if (next.data?.auth === false) {
    return true  // skips all tutorial logic
}
```

**New behavior**:
```typescript
// Public routes without tutorialStep — always allowed
if (next.data?.auth === false && next.data?.tutorialStep === undefined) {
    return true
}

// Routes with tutorialStep (including auth:false tutorial routes) go through tutorial logic
```

**Rationale**: The existing `onboarding/loading` route already has `{ auth: false, tutorialStep: 2 }` but its `tutorialStep` is currently dead code. This fix makes the metadata meaningful and consistent.

**Alternative considered**: Remove `auth: false` from discover route and rely solely on `tutorialStep`. Rejected because the route genuinely needs to be accessible without authentication during onboarding — `auth: false` communicates this intent, while `tutorialStep` gates the tutorial progression.

### 2. Add tutorialStep: 1 to the /discover route

**Decision**: Change the `/discover` route data from `{ auth: false }` to `{ auth: false, tutorialStep: 1 }`.

**Rationale**: Aligns with the existing pattern used by `onboarding/loading` (tutorialStep: 2), `dashboard` (tutorialStep: 3), and `my-artists` (tutorialStep: 5). The `frontend-route-guard` spec already requires this.

### 3. Update spec to use /discover instead of /onboarding/discover

**Decision**: Update the `frontend-route-guard` spec path from `/onboarding/discover` to `/discover` to match the actual route.

**Rationale**: The route has been `/discover` since implementation. Changing the route path would break existing links and add unnecessary churn. The spec should reflect reality.

## Risks / Trade-offs

- **[Risk] Existing tests may assume auth:false routes always pass** → Review auth-hook test cases. The change narrows `auth: false` bypass to routes without `tutorialStep`, which is a behavior change for `onboarding/loading` as well.
- **[Risk] Unauthenticated users who somehow have onboardingStep=0 and navigate to /discover get redirected to landing page** → This is the correct behavior. Users must click "Get Started" to enter the tutorial.
