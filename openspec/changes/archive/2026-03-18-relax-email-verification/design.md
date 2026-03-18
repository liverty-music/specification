## Context

Email verification was implemented as a hard gate across the stack (Zitadel OTP → Frontend callback check → Backend interceptor). With Postmark SMTP now configured, Zitadel's Hosted Login blocks the OIDC authorization flow during Self-Registration until the user completes email OTP verification. On mobile, this requires switching apps to copy a code — a high-friction step that causes abandonment. No current feature requires verified email.

The `email_verified` claim infrastructure (Zitadel Action `add-email-claim.js`, backend `Claims.EmailVerified` field, JWT extraction) should be preserved for future use. Only the enforcement layers are removed.

## Goals / Non-Goals

**Goals:**
- Allow users with `email_verified=false` to use all current features without restriction
- Eliminate the OTP step during Zitadel Self-Registration so the OIDC flow completes immediately
- Optimize the auth callback to avoid unnecessary `Create` RPC calls for returning users
- Preserve `email_verified` claim infrastructure for future per-feature enforcement

**Non-Goals:**
- Building a custom email verification flow (Zitadel handles this)
- Adding in-app email verification prompts (future work, when a feature needs it)
- Removing the Zitadel Action or `Claims.EmailVerified` backend field

## Decisions

### 1. Remove backend `EmailVerificationInterceptor` entirely (not disable)

Delete `email_verification.go`, its test file, and the interceptor chain entry in `connect.go`. The `Claims.EmailVerified` field and its extraction in `JWTValidator` remain — they are read-only and cost nothing.

**Alternative**: Keep the interceptor but with an empty allowlist. Rejected — YAGNI. When a feature needs email verification, it should be enforced at the use-case layer (per-RPC), not as a blanket interceptor. Re-adding a blanket interceptor later would be trivial if needed.

### 2. Remove frontend `email_verified` gate in auth callback

Remove the `email_verified` check and `signOut()` call in `auth-callback-route.ts`. Unverified users proceed through the normal provisioning and redirect flow.

### 3. Refactor frontend provisioning: ensureLoaded-first (B plan)

Current flow calls `provisionUser()` on every callback, relying on `ALREADY_EXISTS` being silently swallowed. Change to:

1. Call `ensureLoaded()` (which calls `UserService.Get` RPC)
2. If the user exists → proceed (no Create RPC needed)
3. If NotFound → call `provisionUser()` → call `ensureLoaded()` again

The NotFound detection happens in the callback handler (not in `ensureLoaded()` itself), since `ensureLoaded()` is a general-purpose method used elsewhere.

**Alternative**: Pass `isSignUp` state through the OIDC flow. Rejected — `oidc-client-ts` does not surface the original `prompt` parameter in the callback `User` object.

### 4. Disable Zitadel email verification during Self-Registration

The `@pulumiverse/zitadel` Pulumi provider's `LoginPolicy` resource does not expose an email verification setting. Zitadel's Hosted Login automatically shows the OTP step when SMTP is configured — there is no policy toggle.

**Approach**: Add a Zitadel Action on the `INTERNAL_AUTHENTICATION / PRE_CREATION` flow that calls `api.setEmailVerified(true)` before the user is created. Since the email is already marked verified at creation time, Zitadel skips the OTP step entirely.

```
Self-Registration Flow:
  1. User enters email
  2. Passkey registration
  3. PRE_CREATION Action fires → api.setEmailVerified(true)
  4. User created with email already verified
  5. No OTP step (email already verified)
  6. OIDC redirect → /auth/callback
```

**Why PRE_CREATION over POST_CREATION**: The `PRE_CREATION` trigger has `setEmailVerified(bool)` in its API, which modifies the user data before creation. `POST_CREATION` only provides `appendUserGrant` — it cannot modify email verification status after creation.

**Trade-off**: With auto-verification, `email_verified` will be `true` from the start for all new users. This means the claim cannot distinguish "actually clicked verification link" from "auto-verified at creation". This is acceptable because:
- No current feature needs to distinguish these states
- If a future feature needs proof-of-email (e.g., sending transactional email), a re-verification flow can be introduced at that point

**Implementation**: New Zitadel Action script `auto-verify-email.js` using the `PRE_CREATION` trigger in the `INTERNAL_AUTHENTICATION` flow.

## Risks / Trade-offs

**[Auto-verify loses email verification signal]** → Acceptable for now. No feature requires verified email. If needed later, re-verification can be triggered per-feature. The Zitadel Action and `email_verified` claim infrastructure remain in place.

**[Zitadel Action API compatibility]** → The `PRE_CREATION` trigger and user verification API depend on Zitadel's Actions runtime. If the API changes, the Action will fail. Mitigation: `allowedToFail: false` in staging/prod blocks token issuance on script error. In dev, `allowedToFail: true` allows iteration.

**[ensureLoaded NotFound race condition]** → If two tabs trigger callback simultaneously, both may see NotFound and call Create. The backend handles this via the existing `ALREADY_EXISTS` graceful handling, so this is safe.
