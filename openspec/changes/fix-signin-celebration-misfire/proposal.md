## Why

The post-signup celebration overlay ("ようこそ！" confetti) and the `PostSignupDialog` bottom sheet fire on **sign-IN** (a returning user logging in), not only on **sign-UP**. This violates `post-signup-dialog` ("Dialog not shown on subsequent logins") and the `onboarding-celebration` intent of a "newly signed-up user" payoff. It presents a jarring first-run experience to established users every time they log in on a fresh browser, a new device, or after clearing storage.

The root cause is that the auth-callback decides "is this a new account?" from the wrong signal: `UserStore.ensureLoaded()` returns `created: true` whenever there is **no cached `user_id` in localStorage**, then falls through to the idempotent backend `Create`. A *returning* user with an empty cache (new browser/device, cleared storage, or guest-browse-then-sign-in — the guest path never caches a `user_id`) therefore looks identical to a brand-new account. The backend `Create` is idempotent and wire-identical for new vs. returning identities (`CreateResponse` carries no "created" field), so the local cache-miss is a fundamentally unreliable proxy for account novelty.

The reliable signal — which button the user actually pressed — was deliberately removed from the OIDC `state` round-trip on the false premise that a backend new-account signal exists. Re-introducing that flow signal fixes the reported sign-in case completely, entirely within the frontend, with no cross-repo/BSR dependency.

## What Changes

- The frontend `signUp()` flow SHALL stamp the OIDC authorization request with an application `state` marker identifying the **sign-up flow** (via `oidc-client-ts` `signinRedirect({ state })`), which round-trips back to `/auth/callback`.
- The auth-callback SHALL set the post-signup "pending" flag (`liverty:postSignup:shown`) **only when the completed flow is the sign-up flow** — i.e. the user arrived via `signUp()` — instead of keying it solely on the `created` cache-miss heuristic.
- As a result, a returning user completing the **sign-in** flow SHALL NOT trigger the celebration overlay or the PostSignupDialog, regardless of local cache state (fresh browser, cleared storage, guest-then-sign-in).
- The celebration overlay (`onboarding-celebration` Tier Z-full) is transitively corrected because it is gated on the same "pending" flag; no behavioral requirement of `onboarding-celebration` changes.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `post-signup-dialog`: The "Post-Signup Dialog on First Authentication" requirement changes the condition under which the post-signup "pending" flag is set — from "provisioned a new user (cache-miss)" to "completed the sign-up flow (OIDC flow signal)". Adds a scenario asserting the flag is NOT set for a returning sign-in with an empty local cache.

## Impact

- **Frontend only** (`liverty-music/frontend`). No proto, backend, or BSR changes.
- `shared/services/auth-service.ts` — `signUp()` adds a `state: { flow: 'signup' }` marker to `signinRedirect`; `handleCallback()` must surface the returned `user.state`.
- `src/routes/auth-callback/auth-callback-route.ts` — gate the `liverty:postSignup:shown = 'pending'` write on the sign-up flow marker.
- No change to `UserStore.ensureLoaded()` provisioning semantics (the guest-follow migration and user hydration paths are untouched); only the celebration-gating decision moves off the `created` proxy.
- Existing unit tests for the auth-callback and (optionally) an e2e sign-in-does-not-celebrate check.
