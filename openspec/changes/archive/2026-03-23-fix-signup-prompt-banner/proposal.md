## Why

The signup-prompt-banner has three bugs that undermine its conversion purpose:
1. The banner background is nearly invisible (5% white opacity on a dark surface), making the entire CTA unnoticeable.
2. On the My Artists page, the banner never appears for unauthenticated users because `showSignupBanner` is not set in the `loading()` lifecycle.
3. The Dashboard calls `TicketJourneyService/ListByUser` without an auth guard, causing a 401 error for unauthenticated users.

These issues collectively mean the signup prompt — the primary conversion mechanism for guest users — is broken on both key pages.

## What Changes

- **Fix banner visibility**: Replace the 5% opacity background with a frosted glass surface (raised surface color at 85% opacity + backdrop blur), add a brand gradient top border, and a glow pulse animation on the CTA button to improve visual prominence.
- **Fix banner display on My Artists**: Add auth-check logic in `my-artists-route.ts` `loading()` to set `showSignupBanner = true` for unauthenticated users who completed onboarding, matching the existing Dashboard pattern.
- **Fix 401 error on Dashboard**: Add an `isAuthenticated` guard in `dashboard-service.ts` `fetchJourneyMap()` to skip the `TicketJourneyService/ListByUser` RPC call for unauthenticated users, returning an empty map instead.
- **Add slide-in entrance animation** for the banner with `prefers-reduced-motion` support.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `signup-prompt-banner`: Visual style requirements change (frosted glass background, gradient border, CTA glow animation, slide-in entrance). No behavioral requirement changes.

## Impact

- **Frontend only**: All changes are in the `frontend` repo.
  - `src/components/signup-prompt-banner/signup-prompt-banner.css` — style overhaul
  - `src/routes/my-artists/my-artists-route.ts` — add banner display logic in `loading()`
  - `src/services/dashboard-service.ts` — add auth guard to `fetchJourneyMap()`
- **No API/proto changes**: The 401 fix is a client-side guard, not a backend change.
- **No breaking changes**.
