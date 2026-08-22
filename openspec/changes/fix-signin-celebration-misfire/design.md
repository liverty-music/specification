## Context

See proposal.md — Why. The frontend auth-callback currently gates the post-signup celebration/dialog on `UserStore.ensureLoaded()`'s `created` flag, which is derived purely from "was a `user_id` cached in localStorage before the call?". Two facts constrain the fix:

1. The backend `Create` RPC is idempotent and returns a wire-identical `CreateResponse` for new and returning identities (no "created" field). The frontend cannot learn account novelty from the response.
2. The OIDC library in use (`oidc-client-ts`) supports an application-defined `state` object on `signinRedirect({ state })` that is persisted (session storage keyed by the OIDC `state` id) and returned intact on the callback via the resolved `User.state`.

`signIn()` and `signUp()` are already distinct methods (`shared/services/auth-service.ts`) invoked from distinct UI affordances. Only the sign-up-flow intent is missing from the callback, having been removed earlier.

## Goals / Non-Goals

**Goals:**
- Move the celebration/dialog gate off the `created` cache-miss proxy and onto a reliable, frontend-only signal of the flow the user initiated (sign-up vs sign-in).
- Guarantee a returning **sign-in** never triggers the first-run celebration/dialog, regardless of local cache state.
- Keep the change contained to the auth flow; do not alter provisioning, guest-follow migration, or user hydration.

**Non-Goals:**
- Perfect account-novelty detection. "Flow intent" is not identical to "backend minted a fresh row": a returning user who deliberately taps "Sign up" is out of scope for suppression here (rare and low-harm). A truly perfect signal would require a backend `created` field (a separate, cross-repo change) and is explicitly deferred.
- Changing the `UserStore.ensureLoaded()` return shape or removing its `created` flag (it may still be used to further narrow the gate; see Decisions).
- Any change to `onboarding-celebration` behavior — it remains gated on the same `liverty:postSignup:shown` flag and is fixed transitively.

## Decisions

### D1: Carry the flow intent through OIDC `state`, not `prompt`

`signUp()` already sends `prompt: 'create'` to Zitadel, but `prompt` is a request-only hint and is **not** echoed to the callback. Use the app `state` round-trip instead: `signUp()` calls `signinRedirect({ prompt: 'create', state: { flow: 'signup' } })`. `handleCallback()` resolves the OIDC `User` (whose `.state` is the original object) and exposes the flow marker to `AuthCallbackRoute`.

- **Alternative — re-derive from `prompt` on the callback:** not possible; `prompt` is not returned.
- **Alternative — a separate `localStorage`/`sessionStorage` breadcrumb written by `signUp()`:** works, but duplicates state the OIDC library already round-trips reliably and risks desync across tabs/redirect edge cases. The OIDC `state` channel is purpose-built for exactly this.

### D2: Gate the pending flag on `flow === 'signup'`

In `AuthCallbackRoute`, set `localStorage['liverty:postSignup:shown'] = pending` only when the resolved flow marker is `'signup'`. The `signIn()` path (default, or `prompt: 'login'` in DEV) carries no such marker → the flag is never set on sign-in.

- **Optional narrowing (recommended): `flow === 'signup' && created`.** Keeping the existing `created` cache-miss as an additional AND-condition also suppresses the residual "returning user taps Sign up on a device that already cached their id" case, at zero extra cost. It never re-introduces the sign-in bug because the sign-in flow already fails the first condition. Final choice recorded in tasks; default to the AND form.

### D3: Backward/robustness for a missing marker

A callback with **no** flow marker (older in-flight redirect started before deploy, or a direct `/auth/callback` hit) SHALL be treated as **not** sign-up (fail closed → no celebration). This is the safe default: at worst a brand-new user who somehow lost the marker misses the confetti; no returning user is ever wrongly celebrated.

## Risks / Trade-offs

- **[Returning user deliberately taps "Sign up" → sees first-run payoff]** → Mitigated by the D2 optional AND-`created` narrowing for the common same-device case; the cross-device residue is rare and harmless. Full correctness deferred to a future backend `created` signal.
- **[A brand-new user's marker is lost (blocked storage, cross-tab redirect anomaly) → misses the celebration]** → Accepted; fail-closed per D3. Missing a one-time confetti is strictly less harmful than the current false-positive on every returning sign-in.
- **[OIDC `state` serialization limits]** → `state` must be JSON-serializable; a small `{ flow: 'signup' }` object is well within `oidc-client-ts` support and its session-storage persistence.

## Migration Plan

- Pure frontend deploy; no data migration, no proto/BSR. Standard frontend release path.
- Rollback: revert the frontend change; behavior returns to the prior `created`-only gate.
- No feature flag needed; the change is self-contained and fail-closed.
