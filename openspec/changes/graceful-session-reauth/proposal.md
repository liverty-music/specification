## Why

After a session sits idle past the 30-minute access-token lifetime, the first
RPC an operator triggers fails with a raw `Unauthenticated` error — surfaced to
the admin console user as the literal backend string
`invalid token: failed to validate token: "exp" not satisfied` (observed live,
2026-08-21, creating an Organizer). The app *does* recover on the next attempt
(the on-`Unauthenticated` refresh works — verified: `org-test-11` was created
after a single 401→refresh→retry), but the user still sees a scary console
error and, intermittently, a rendered error in the UI.

Root cause (confirmed by server logs + browser console, not assumed): the
frontend refreshes the token at exactly two points — boot, and reactively on an
RPC `Unauthenticated`. There is **no refresh when the app resumes from idle**.
So the token is allowed to go cold; the first foreground action after idle
always 401s. The fan-web SPA hides this because it constantly re-fetches and has
a `visibilitychange` resume-revalidator that warms the token before the user
acts; the admin and organizer consoles have neither, so an idle-then-mutate is
the one place the cold-token 401 is visible.

The naive fix — enabling `automaticSilentRenew` — does NOT work here: the
existing spec already documents (citing oidc-client-ts #2012) that the background
timer abandons renewal once the token is already expired, and browsers throttle
background-tab timers so it never fires during idle. The correct, ecosystem-aligned
fix is a **resume-time silent refresh** (refresh on `visibilitychange` when the
token is expired/near-expiry, before any RPC), plus never surfacing a raw auth
error to the user.

## What Changes

- Add a **third silent-refresh trigger** to the shared auth service: on
  `visibilitychange` to `visible` (app resumes to the foreground), if the stored
  access token is expired or within a small skew window of expiry, perform a
  single silent refresh (`signinSilent()`) **before** the user's next RPC —
  mirroring the boot-time `restoreSession()` behavior that already works (and is
  why a manual reload fixes the error today).
- Keep `automaticSilentRenew` **disabled** (the service-worker-reload refresh-token
  rotation race that motivated disabling it is unchanged); the resume refresh
  reuses the existing single-flight dedup so it cannot double-spend a rotating
  refresh token.
- Make `Unauthenticated` recovery **silent**: a token-expiry error that is (or
  can be) recovered SHALL NOT render a raw backend error string to the user. On
  unrecoverable expiry (refresh token itself dead), the app SHALL present a
  neutral "session expired — signing you back in" state and route to
  re-authentication, never the raw `"exp" not satisfied` text.
- Apply uniformly via the shared `auth-service.ts` so all three entries
  (consumer/fan-web, admin, organizer) get the same behavior; the consumer's
  existing resume-revalidator continues to work and is complementary.

Explicit non-goals: enabling `automaticSilentRenew`; a background renewal timer;
migrating to a BFF / server-side token model; changing Zitadel token lifetimes.

## Capabilities

### New Capabilities
<!-- None. This refines existing authentication behavior. -->

### Modified Capabilities
- `authentication`: the **Silent token refresh strategy** requirement changes
  from "refresh at exactly two points (boot, on-`Unauthenticated`)" to add a
  third point — **resume-time refresh on `visibilitychange`** — and a new
  requirement that auth-expiry recovery is graceful (no raw backend error text
  surfaced to the user).

## Impact

- **frontend** (`shared/services/auth-service.ts` + a small resume hook): a
  `visibilitychange`-triggered silent refresh guarded by an expiry check and the
  existing refresh dedup; graceful mapping of `Unauthenticated` so no raw error
  string reaches the UI. Affects the consumer, admin, and organizer entries
  (shared surface). No proto, no BSR, no backend changes.
