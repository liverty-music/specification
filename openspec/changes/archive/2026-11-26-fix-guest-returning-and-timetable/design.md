## Context

Guest state lives in `OnboardingService` (one latched flag, `onboardingComplete`, set on the first timetable arrival with at least one follow, or at sign-in) and `FollowStore` (guest follow queue hydrated from localStorage). Welcome's `canLoad` redirects signed-in fans only. `roam-app-as-guest` requires that a guest still in onboarding can reach Welcome, and Welcome's `[Log In]` discards guest follows and home on purpose (frontend#857 is still open on that).

## Decisions

1. **Returning guest = onboarding complete and at least one guest follow.** `isCompleted` alone would also catch a fan who signed out (the flag stays true, the follow queue is empty) and would send a guest back to an empty timetable after a cancelled `[Log In]`; requiring a follow keeps both on Welcome, where the Log In button is. A guest with follows who has not yet reached the timetable is still in onboarding and keeps Welcome, as `roam-app-as-guest` requires.
2. **The guest date bound is cut on the client.** The guest read is `ListByArtists`, whose spec says "past and upcoming" and which the Welcome preview and others use as is; adding a bound needs a proto change. The cut runs after the cache, so a look-back `from` still sees every date from the cached result.
3. **Add, not modify, the timetable requirement.** `globalize-venues` rewrites "Default today-onward timetable"; a separate ADDED requirement merges with it without a conflict.
