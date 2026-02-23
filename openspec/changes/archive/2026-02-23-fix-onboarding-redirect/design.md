## Context

The current onboarding completion check (`OnboardingService.hasCompletedOnboarding()`) calls `ArtistService.ListFollowed` and returns `true` if the user follows at least one artist. This conflates "has followed artists" with "has completed onboarding", causing users who unfollow all artists to be sent back to the discovery page.

The `auth-callback.ts` already tracks whether a login is a sign-up via OIDC state (`{ isSignUp: true }`). This existing signal is sufficient to determine the correct routing target without any backend changes.

Additionally, `localStorage['liverty:onboarding_complete']` is set in `artist-discovery-page.ts` but never read — dead code from a previous implementation.

## Goals / Non-Goals

**Goals:**
- Fix the re-onboarding bug: existing users who unfollow all artists stay on the dashboard
- Simplify routing logic by using the existing `isSignUp` OIDC state flag
- Remove dead code (`ONBOARDING_COMPLETE_KEY`)
- Eliminate the unnecessary `ListFollowed` RPC call on every authentication

**Non-Goals:**
- Persisting onboarding state to the database (not needed for this fix)
- Restricting access to `/onboarding/discover` for existing users (URL direct access is acceptable as a "re-discover" experience)
- Changing the region selection overlay logic (independent system, unaffected)
- Modifying backend or protobuf definitions

## Decisions

### Decision 1: Use `isSignUp` OIDC state for routing instead of `ListFollowed` RPC

**Choice**: Route based on `state.isSignUp` in `auth-callback.ts`. Sign-up → discover, sign-in → dashboard.

**Alternatives considered**:
- **Add `onboarding_completed_at` to DB**: Correct and durable, but requires migration, proto changes, backend changes — overengineered for this problem.
- **Use `sessionStorage`/`localStorage` flag**: Works but introduces client-side state management that can diverge across devices/browsers.

**Rationale**: The `isSignUp` flag already exists in the OIDC flow. It precisely captures the distinction we need (new user vs returning user) without any new state to manage. The sign-up flow is the only entry point to onboarding — using it directly eliminates the false equivalence between "followed artists" and "completed onboarding".

### Decision 2: Simplify `welcome-page.ts` canLoad to always redirect to dashboard

**Choice**: When an authenticated user hits `/` or `/welcome`, always redirect to `/dashboard`.

**Rationale**: The welcome page's purpose is to prompt unauthenticated users to sign in/up. Authenticated users should never see it. The previous `getRedirectTarget()` call (which checked followed artists) is no longer needed since onboarding routing is handled exclusively in `auth-callback.ts`.

### Decision 3: Keep `loading-sequence.ts` canLoad guard intact

**Choice**: The loading sequence guard that checks local `followedArtists` state remains unchanged.

**Rationale**: This guard serves a different purpose — it prevents users from accessing the loading sequence without having selected artists in the discovery step. It validates the in-progress onboarding flow, not onboarding completion status.

### Decision 4: Allow discover page access for existing users

**Choice**: Do not add route guards to block authenticated users from `/onboarding/discover`.

**Rationale**: If an existing user navigates to discover via URL, showing the page is acceptable as a "re-discover" experience. Adding guards would require state tracking that we're explicitly trying to avoid.

## Risks / Trade-offs

- **[Risk] User signs up but closes browser before completing discover** → On next login, they sign in (not sign up), so they go to dashboard with no followed artists. Dashboard shows empty state with region overlay. This is acceptable — the user can navigate to discover or follow artists from other entry points in the future.

- **[Trade-off] No server-side onboarding record** → We cannot query "has this user completed onboarding" from the backend. This is fine for the current scope where only the frontend cares about this routing decision. If a backend need arises later, we can add the DB field then.

- **[Risk] `provisionUser` fails but auth succeeds** → Current behavior already handles this gracefully (logs error, continues flow). The user still gets routed to discover on sign-up. On retry sign-in, `provisionUser` is not called, and the user goes to dashboard. The existing `AlreadyExists` handling covers the case where provisioning eventually succeeds on a subsequent sign-up attempt.
