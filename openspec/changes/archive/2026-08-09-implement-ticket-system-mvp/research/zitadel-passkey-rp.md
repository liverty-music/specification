# Zitadel as WebAuthn/Passkey Relying Party — Research

> Researched: 2026-02-20
> Purpose: Evaluate whether Zitadel can serve as the WebAuthn RP for the ticket system MVP

## Summary

Zitadel supports Passkey registration and authentication via its v2 API. However, critical
limitations exist around custom Login UI on separate domains (Issue #8282), credential public
key export (not possible), and Conditional UI / autofill (not supported).

## A. Passkey Registration Flow

**Source**: [Zitadel Docs - RegisterPasskey API](https://zitadel.com/docs/apis/resources/user_service_v2/user-service-register-passkey)

**Endpoint**: `POST /v2/users/{user_id}/passkeys`

**Request**:
- `code` (optional): Registration code for email-link flows
- `authenticator` (optional): `PASSKEY_AUTHENTICATOR_UNSPECIFIED` | `PASSKEY_AUTHENTICATOR_PLATFORM` | `PASSKEY_AUTHENTICATOR_CROSS_PLATFORM`
- `domain` (optional): Domain specification

**Response** (HTTP 200):
- `passkeyId`: Registered passkey ID
- `publicKeyCredentialCreationOptions`: WebAuthn credential creation options — can be passed directly to `navigator.credentials.create()`

**Verification**: `POST /v2/users/{user_id}/passkeys/{passkey_id}` with `publicKeyCredential` from browser. Zitadel stores the credential public key internally.

## B. Passkey Authentication Flow (Session API)

**Source**: [Zitadel Docs - Passkey Login UI](https://zitadel.com/docs/guides/integrate/login-ui/passkey)

3-step flow:

1. **Create session + request challenge**:
   ```
   POST /v2/sessions
   {
     "checks": { "user": { "loginName": "user@example.com" } },
     "challenges": {
       "webAuthN": {
         "domain": "example.domain.com",
         "userVerificationRequirement": "USER_VERIFICATION_REQUIREMENT_REQUIRED"
       }
     }
   }
   ```
   Response includes `sessionId`, `sessionToken`, `challenges.webAuthN.publicKeyCredentialRequestOptions`.

2. **Browser authentication**: `navigator.credentials.get({ publicKey: publicKeyCredentialRequestOptions })`

3. **Update session with assertion**:
   ```
   PATCH /v2/sessions/{sessionId}
   { "checks": { "webAuthN": { "credentialAssertionData": { ... } } } }
   ```

### Session → OIDC Token Exchange

**Source**: [Zitadel Docs - Session API Guide](https://zitadel.com/docs/guides/integrate/login-ui/session-api)

Authenticated session can finalize an OIDC auth request:
```
POST /v2/oidc/auth_requests/{authRequestId}
{ "sessionId": "...", "sessionToken": "..." }
```
Returns callback URL with authorization code → standard OIDC token exchange.

## C. Credential Public Key Access

**Source**: [Zitadel Docs - ListPasskeys API](https://zitadel.com/docs/apis/resources/user_service_v2/user-service-list-passkeys)

`POST /v2/users/{user_id}/passkeys/_search` returns ONLY:
- `id` (string)
- `state` (enum)
- `name` (string)

**Credential public key, credential ID binary, and other cryptographic material are NOT exposed.**

This means:
- Cannot derive Safe address from credential public key via Zitadel
- Cannot perform independent WebAuthn assertion verification outside Zitadel
- Must use an alternative derivation source (e.g., Zitadel user ID / sub claim)

## D. RPID and Domain Constraints

### How RPID is determined

**Source**: [Zitadel source code - webauthn.go](https://github.com/zitadel/zitadel/blob/main/internal/webauthn/webauthn.go)

- If `domain` parameter is provided: used directly as RPID
- If `domain` is empty: derived from HTTP request context (`RequestedDomain()`)

### Domain change warning

**Source**: [Zitadel Docs - Passkeys Concept](https://zitadel.com/docs/concepts/features/passkeys)

> "Passkey authentication is based on the domain, if you change it, your users will not be able
> to login with the registered passkey authentication."

Recommendation: Configure custom domain BEFORE enabling Passkeys.

### CRITICAL BUG: Issue #8282 (Open, Unresolved)

**Source**: [GitHub Issue #8282](https://github.com/zitadel/zitadel/issues/8282)

**Status**: Open (assigned to peintnermax)

**Problem**: When `domain` parameter is passed to Session API, `RPOrigins` is set to `[""]`
(empty string) in `webauthn.go`. This causes go-webauthn to fail origin validation → 500 error.

```
Session API: domain="login.example.com"
  → serverFromContext(ctx, "login.example.com", "")
  → config: { RPID: "login.example.com", RPOrigins: [""] }
  → go-webauthn: origin "" != actual origin → 500 error
```

**Workaround**: Zitadel's own TypeScript Login app passes `""` (empty string) for domain,
but this bypasses protobuf validation (min 1 char) via internal routing. External API callers
cannot use this workaround.

**Impact**: Custom Login UI hosted on a different domain than Zitadel cannot reliably use
Passkey authentication via Session API.

### PR #6097 (Merged, 2023-06-27)

**Source**: [GitHub PR #6097](https://github.com/zitadel/zitadel/pull/6097)

Added the `domain` parameter to Session API specifically for the use case:
> "This is useful in cases where the login UI is served under a different domain / origin
> than the ZITADEL API."

The intent was correct, but the implementation has the RPOrigins bug described above.

## E. Custom Login UI Implementation

**Source**: [Zitadel Docs - Custom Login UI](https://zitadel.com/docs/guides/integrate/login-ui)

Full flow:
1. App redirects to Login UI via OIDC authorize request
2. Zitadel redirects to `/login?authRequest={id}`
3. Login UI creates and authenticates a session via Zitadel v2 APIs
4. Login UI finalizes the auth request: `POST /v2/oidc/auth_requests/{authRequestId}`
5. Browser redirected back to app with authorization code

Requirements:
- OIDC endpoints must be proxied to Zitadel
- Next.js reference implementation exists
- Backend uses service account PAT for policy retrieval

## F. Limitations and Known Issues

| Limitation | Source | Impact |
|---|---|---|
| domain parameter bug (RPOrigins empty) | Issue #8282 (Open) | Custom Login UI on different domain broken |
| Credential public key not exported | ListPasskeys API docs | Cannot use credential for on-chain derivation |
| Domain change invalidates all Passkeys | Passkeys concept docs | Must finalize domain before enabling |
| Conditional UI (autofill) not supported | Discussion #8867, Issue #8899 | Cannot implement passwordless autofill UX |
| Related Origins (.well-known/webauthn) not supported | No Issue/FR exists | No cross-origin Passkey sharing |
| Self-hosted vs Cloud differences | Not documented | Unknown feature parity |

## Sources

- [Zitadel Docs: Passkeys Concept](https://zitadel.com/docs/concepts/features/passkeys)
- [Zitadel Docs: RegisterPasskey API](https://zitadel.com/docs/apis/resources/user_service_v2/user-service-register-passkey)
- [Zitadel Docs: VerifyPasskeyRegistration API](https://zitadel.com/docs/apis/resources/user_service_v2/user-service-verify-passkey-registration)
- [Zitadel Docs: CreateSession API](https://zitadel.com/docs/apis/resources/session_service_v2/session-service-create-session)
- [Zitadel Docs: Custom Login UI Guide](https://zitadel.com/docs/guides/integrate/login-ui)
- [Zitadel Docs: Passkey Login UI Guide](https://zitadel.com/docs/guides/integrate/login-ui/passkey)
- [Zitadel Docs: Session API Guide](https://zitadel.com/docs/guides/integrate/login-ui/session-api)
- [PR #6097: fix: provide domain in session, passkey and u2f](https://github.com/zitadel/zitadel/pull/6097)
- [Issue #8282: WebAuthN.BeginLoginFailed (Open)](https://github.com/zitadel/zitadel/issues/8282)
- [Issue #4307: WebAuthN not working behind NGINX](https://github.com/zitadel/zitadel/issues/4307)
- [Issue #7251: WebAuthN with example nginx config](https://github.com/zitadel/zitadel/issues/7251)
- [Discussion #8867: Passkey Autofill UI](https://github.com/zitadel/zitadel/discussions/8867)
- [Issue #8899: Passkey Autofill UI Feature Request](https://github.com/zitadel/zitadel/issues/8899)
- [Zitadel Community Q&A: WebAuthN begin login failed](https://questions.zitadel.com/m/1383062464924483656)
- [Zitadel WebAuthn source code](https://github.com/zitadel/zitadel/blob/main/internal/webauthn/webauthn.go)
