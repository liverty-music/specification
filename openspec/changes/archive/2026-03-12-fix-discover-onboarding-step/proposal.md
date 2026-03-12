## Why

The `/discover` route is missing `tutorialStep: 1` in its route metadata, causing `onboarding.isOnboarding` to return `false` for unauthenticated tutorial users. This means the `FollowServiceClient` bypasses the localStorage fallback and calls the backend RPC directly, resulting in a 401 "missing bearer token" error every time a guest user tries to follow an artist during onboarding.

The `frontend-route-guard` spec explicitly requires `/onboarding/discover` to have `tutorialStep: 1`, but the current implementation defines the route as `/discover` with `data: { auth: false }` only.

## What Changes

- Add `tutorialStep: 1` to the `/discover` route metadata in `my-app.ts` so that the auth hook correctly sets `onboardingStep` to `DISCOVER` when navigating directly to the route
- Align the route path with the spec (`/onboarding/discover` vs `/discover`) or update the spec to match the actual path — requires decision

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `frontend-route-guard`: The `/discover` route definition must include `tutorialStep: 1` metadata to match the existing spec requirement. If the route path remains `/discover` instead of `/onboarding/discover`, the spec must be updated to reflect the actual path.

## Impact

- **Frontend**: `my-app.ts` route configuration, `auth-hook.ts` behavior for `/discover`
- **No backend changes**: The `FollowServiceClient` branching logic is already correct — it just needs `isOnboarding` to return `true`
- **No breaking changes**: This is a bug fix restoring intended behavior
