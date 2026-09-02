# Authentication Capability

## Purpose

JWT-based authentication for user-specific operations in the backend. This capability validates JWT tokens from ZITADEL using their JWKS endpoint to authenticate API requests and scope operations to individual users.
## Requirements
### Requirement: Silent token refresh strategy
The frontend SHALL refresh access tokens silently at three points, and SHALL
NOT run a proactive background renewal timer (`automaticSilentRenew` stays
disabled): (1) at boot, if the stored access token is already expired; (2) on
**resume to the foreground** (`visibilitychange` to `visible`), if the stored
access token is expired or within a small skew window of expiry; (3) reactively,
when an RPC returns `Unauthenticated`.

**Reactive refresh contract**: when an authenticated caller's RPC returns
`Unauthenticated`, the app SHALL perform a silent refresh and then **retry the
original request once** with the new access token. The retry is bounded to a
single attempt per request: if the retried request also returns
`Unauthenticated`, the app SHALL NOT refresh-and-retry again (no unbounded
loop) — it SHALL treat the session as unrecoverable (see *Graceful session
re-authentication*).

**Single-flight**: all three refresh points, and every concurrent trigger within
them, SHALL share **one** in-flight refresh so that at most one `signinSilent()`
runs at a time. This includes the boot-time restore and the reactive interceptor:
an early RPC that 401s while boot-time restore is still in flight MUST join the
in-flight refresh rather than start a second, concurrent `signinSilent()`. This
single-flight guarantee is the direct antidote to the Zitadel refresh-token
rotation race the disabled background timer was avoiding.

**Rationale**: With Zitadel refresh token rotation, a *background timer* running
concurrently with a service-worker page reload causes both the old and new page
to use the same refresh token, resulting in `RefreshTokenInvalid (400)` and
forced logout — so the timer stays off. The resume-time refresh is NOT a timer:
it fires only on an explicit foreground-resume event, at most once per resume,
through the shared single-flight guard, so it does not reintroduce the rotation
race. It closes the gap the timer cannot cover — `oidc-client-ts`
`automaticSilentRenew` abandons renewal once the access token is already expired
(issue #2012) and browsers throttle background-tab timers, so neither would
refresh a token that went cold while the tab was idle. Resume-time refresh warms
the token *before* the user's next action, mirroring the boot-time restore that
already makes a manual reload recover the session.

#### Scenario: Boot with valid access token
- **WHEN** the app boots and the stored access token is not expired
- **THEN** the app SHALL proceed without calling `signinSilent()`

#### Scenario: Boot with expired access token
- **WHEN** the app boots and the stored access token is expired
- **THEN** the app SHALL call `signinSilent()` once via `restoreSession()`
- **AND** if `signinSilent()` succeeds, the user session SHALL be restored transparently
- **AND** if `signinSilent()` fails, the user SHALL start the session unauthenticated

#### Scenario: Resume from idle with an expired access token
- **WHEN** the app returns to the foreground (`visibilitychange` to `visible`)
  after an idle period
- **AND** the stored user is authenticated but the access token is expired or
  within the skew window of expiry
- **THEN** the app SHALL perform a single silent refresh before the user's next
  RPC
- **AND** if it succeeds, subsequent RPCs SHALL use the fresh token with no
  visible interruption
- **AND** the refresh SHALL be de-duplicated with any in-flight refresh (at most
  one `signinSilent()` for concurrent triggers)

#### Scenario: Resume with a still-valid access token
- **WHEN** the app returns to the foreground and the stored access token is not
  expired and not within the skew window
- **THEN** the app SHALL NOT trigger a resume-time refresh

#### Scenario: No background timer
- **WHEN** the access token is about to expire during an active, foreground session
- **THEN** the app SHALL NOT proactively refresh the token on a timer
- **AND** the token SHALL be refreshed on the next resume event or the next RPC
  that receives `Unauthenticated`, whichever comes first

#### Scenario: Reactive refresh retries the original request once
- **WHEN** an authenticated caller's RPC returns `Unauthenticated`
- **THEN** the app SHALL perform a silent refresh
- **AND** if the refresh succeeds, the app SHALL retry the original request once
  with the new access token
- **AND** the retried request's result SHALL be returned to the caller (a success
  is transparent; the caller never observes the initial `Unauthenticated`)

#### Scenario: Refresh-and-retry is bounded to once per request
- **WHEN** the retried request also returns `Unauthenticated`
- **THEN** the app SHALL NOT trigger another refresh-and-retry for that request
- **AND** the session SHALL be treated as unrecoverable

#### Scenario: Concurrent triggers share one refresh (single-flight)
- **WHEN** multiple refresh triggers occur close together (e.g. several RPCs
  return `Unauthenticated` at once, or a resume event coincides with an
  in-flight boot-time restore)
- **THEN** the app SHALL execute at most one `signinSilent()` call
- **AND** all waiting callers SHALL observe the result of that single refresh

### Requirement: JWT Token Validation

The system SHALL validate JWT tokens from ZITADEL using the JWKS endpoint.

**Rationale**: Industry-standard JWT validation ensures secure authentication without requiring direct integration with the identity provider for every request.

#### Scenario: Valid Token

- **WHEN** a request includes a valid JWT token in the Authorization header
- **THEN** the system validates the token signature using ZITADEL's public keys
- **AND** verifies the issuer matches the configured ZITADEL instance
- **AND** verifies the token has not expired
- **AND** extracts the user ID from the `sub` claim
- **AND** extracts the `email_verified` claim from the token's private claims

#### Scenario: Invalid Token

- **WHEN** a request includes an invalid or expired JWT token
- **THEN** the system rejects the request with `connect.CodeUnauthenticated`
- **AND** logs the authentication failure for security monitoring

### Requirement: User ID Propagation

The system SHALL extract the user ID from validated tokens and propagate it through the request context.

**Rationale**: Handlers need access to the authenticated user ID to scope operations correctly (e.g., following artists, viewing followed content). The `external_id` (Zitadel `sub`) enables identity resolution against the local database.

#### Scenario: Authenticated Request

- **WHEN** a JWT token is successfully validated
- **THEN** the system extracts the user ID from the token's `sub` claim
- **AND** adds the user ID to the request context as `external_id`
- **AND** makes the user ID accessible to downstream handlers

### Requirement: Authenticated Endpoint Protection

The system SHALL enforce authentication for all RPC endpoints by default using `connectrpc/authn-go` HTTP middleware with default-deny semantics. Unauthenticated requests SHALL be rejected at the HTTP layer before reaching the Connect interceptor chain.

**Rationale**: Default-deny is safer than opt-in protection. The `authn-go` middleware operates at the HTTP layer, rejecting invalid requests before they consume interceptor resources. This eliminates the risk of unprotected endpoints caused by missing handler-level checks.

#### Scenario: Request without Authorization header

- **WHEN** a request to any RPC endpoint does not include an Authorization header
- **THEN** the system SHALL reject the request with `connect.CodeUnauthenticated`
- **AND** the request SHALL NOT reach the Connect interceptor chain or RPC handler

#### Scenario: Request with valid Authorization header

- **WHEN** a request includes a valid `Authorization: Bearer <token>` header
- **THEN** the `authn-go` middleware SHALL validate the token via the existing JWT validator
- **AND** extract claims (sub, email, name) from the token
- **AND** make the claims available to downstream handlers via `authn.GetInfo(ctx)`
- **AND** a bridge interceptor SHALL convert claims into the existing `auth.WithClaims(ctx)` format
- **AND** the request SHALL proceed to the Connect interceptor chain and RPC handler

#### Scenario: Request with invalid Authorization header

- **WHEN** a request includes an invalid, expired, or malformed JWT token
- **THEN** the system SHALL reject the request with `connect.CodeUnauthenticated`
- **AND** the request SHALL NOT reach the Connect interceptor chain or RPC handler

#### Scenario: Claims bridge interceptor position in chain

- **WHEN** the Connect interceptor chain processes a request
- **THEN** the `ClaimsBridgeInterceptor` SHALL run after the panic recovery interceptor and before the validation interceptor
- **AND** the `ClaimsBridgeInterceptor` SHALL have access to OTel trace context in its `ctx` argument

### Requirement: Public Endpoint Access

The system SHALL allow public access to the gRPC health check endpoint without authentication by serving it on a separate HTTP mux outside the `authn-go` middleware boundary.

**Rationale**: Kubernetes liveness/readiness probes must reach the health endpoint without providing authentication credentials. Separating the health check mux from the protected mux keeps the default-deny semantics clean.

#### Scenario: Health check without token

- **WHEN** a Kubernetes probe sends a health check request without an Authorization header
- **THEN** the system SHALL process the request successfully
- **AND** return the health status without requiring authentication

#### Scenario: RPC endpoint without token

- **WHEN** a request to any non-health RPC endpoint (e.g., ArtistService/Search) does not include an Authorization header
- **THEN** the system SHALL reject the request with `connect.CodeUnauthenticated`

### Requirement: Email Verified Claim Injection

The system SHALL inject the `email_verified` claim into JWT access tokens via a Zitadel Action at the `PRE_ACCESS_TOKEN_CREATION` trigger, alongside the existing `email` claim.

**Rationale**: Zitadel does not include `email_verified` in access tokens by default. The claim is preserved for future per-feature enforcement even though no current feature requires it.

#### Scenario: Human user with verified email

- **WHEN** a human user with a verified email address requests an access token
- **THEN** the Zitadel Action SHALL set `email_verified` claim to `true` in the access token

#### Scenario: Human user with unverified email

- **WHEN** a human user with an unverified email address requests an access token
- **THEN** the Zitadel Action SHALL set `email_verified` claim to `false` in the access token

#### Scenario: Machine user (service account)

- **WHEN** a machine user requests an access token
- **THEN** the Zitadel Action SHALL skip `email_verified` injection (no `human` field present)
- **AND** the token SHALL be issued without the `email_verified` claim

### Requirement: Validate Zitadel Actions v2 Webhook JWTs by Signature

The backend SHALL validate the authenticity of incoming Zitadel Actions v2 webhook requests by verifying the JWT payload body against the same JWKS endpoint that the backend already trusts for end-user access-token validation. The validator SHALL enforce signature + expiry checks only; it SHALL NOT enforce `iss` or `aud` claims because Zitadel v4 webhook JWTs do not populate them.

**Rationale**: The Actions v2 webhook authentication model uses Zitadel-signed JWTs (`PAYLOAD_TYPE_JWT`) in place of a shared HMAC secret. Reusing the existing JWKS trust chain gives asymmetric-key verification without adding a rotatable shared secret or a second trust anchor.

The original spec pinned a per-endpoint `aud` claim (e.g., `urn:liverty-music:webhook:pre-access-token`) as the security boundary against access-token replay, on the assumption that webhook JWTs carried OIDC-shaped claims. **Empirically Zitadel v4 webhook JWTs carry only application-specific private claims plus standard `exp` / `iat`** — `iss` comes through as empty string, `aud` as empty array. Both checks rejected every webhook call until they were dropped (backend#288, backend#289).

The replacement security boundary is a defense-in-depth stack:

1. **JWT signature (JWKS)** — proves origin: only Zitadel holds the corresponding private key.
2. **Network isolation** — the webhook listener is `:9090` ClusterIP-only (see `zitadel-action-webhook` spec).
3. **Per-handler payload-shape checks** — each handler decodes handler-specific private claims; a webhook JWT minted for a different purpose would fail downstream payload validation even if signature passes.

End-user access-token replay against the webhook is mitigated by network isolation (an external attacker cannot reach `:9090`) plus payload-shape mismatch (an end-user access token does not carry `user.human.email` in the same nesting Zitadel uses for webhook payloads).

#### Scenario: Webhook request with valid JWT signature passes verification

- **WHEN** the backend receives a webhook request whose body is a JWT signed by the configured Zitadel instance
- **THEN** the backend SHALL verify the JWT signature using the Zitadel JWKS
- **AND** the backend SHALL verify the token has not expired
- **AND** the backend SHALL proceed to process the webhook payload
- **AND** the backend SHALL NOT reject the request based on `iss` or `aud` claim contents

#### Scenario: Webhook request with invalid signature is rejected

- **WHEN** the backend receives a webhook request whose JWT signature is invalid, has expired, or is malformed
- **THEN** the backend SHALL reject the request with HTTP 401
- **AND** the backend SHALL NOT act on the webhook payload

#### Scenario: Webhook JWT validator shares the existing JWKS cache

- **WHEN** the backend services a webhook request
- **THEN** the validator SHALL use the same JWKS cache and refresh cadence (default `15m`) already established for end-user access-token validation
- **AND** the validator SHALL NOT open a separate HTTP client or cache for webhook verification

> **Forward compatibility**: If a future Zitadel version adds proper `iss` / `aud` claims to webhook JWTs, the validator can re-introduce these checks without breaking the existing contract — the current implementation silently accepts any value (including missing). When that happens, this requirement should be tightened to enforce them.

### Requirement: JWKS Caching

The system SHALL cache JWKS keys and auto-refresh them periodically.

**Rationale**: Fetching public keys on every request would add unacceptable latency. Caching with periodic refresh balances security (key rotation) with performance.

**Acceptance Criteria**:
- Default refresh interval: 15 minutes
- Configurable via `JWT_JWKS_REFRESH_INTERVAL` environment variable
- Initial fetch on startup with validation before server accepts requests

#### Scenario: JWKS cache initialized on startup and refreshed periodically

- **WHEN** the server starts
- **THEN** the system SHALL fetch and validate JWKS keys before accepting requests
- **AND** the system SHALL refresh the cached keys on the interval set by `JWT_JWKS_REFRESH_INTERVAL` (default 15 minutes)

### Requirement: Token Validation Performance

The system SHALL complete token validation within 100ms under normal conditions.

**Rationale**: Authentication adds overhead to every authenticated request. Keeping validation fast ensures acceptable API response times.

**Acceptance Criteria**:
- P95 latency for token validation: < 100ms
- Uses efficient JWT parsing library (`github.com/lestrrat-go/jwx/v2`)
- JWKS cache minimizes network calls

#### Scenario: Token validation stays within the latency budget

- **WHEN** an authenticated request is validated under normal conditions
- **THEN** the system SHALL complete token validation within 100ms (P95 < 100ms)
- **AND** the system SHALL parse the JWT locally using the cached JWKS without a per-request network call

### Requirement: Authentication Error Handling

The system SHALL return `connect.CodeUnauthenticated` for failed authentication attempts.

**Rationale**: Consistent error codes allow clients to handle authentication failures uniformly (e.g., redirecting to login).

#### Scenario: Missing Authorization Header

- **WHEN** an authenticated endpoint is called without an Authorization header
- **THEN** the system returns `connect.CodeUnauthenticated` with message "missing authorization header"

#### Scenario: Malformed Token

- **WHEN** the Authorization header contains a malformed token
- **THEN** the system returns `connect.CodeUnauthenticated` with message "invalid token"

#### Scenario: Expired Token

- **WHEN** the JWT token has expired
- **THEN** the system returns `connect.CodeUnauthenticated` with message "token expired"

### Requirement: Graceful session re-authentication
The frontend SHALL NOT surface a raw backend authentication error (for example
the literal string `invalid token: failed to validate token: "exp" not
satisfied`) to the user. When an RPC fails with `Unauthenticated`, the app SHALL
attempt silent recovery (refresh + retry) transparently; a successful recovery
SHALL be invisible to the user. When recovery is not possible (the refresh token
itself is expired or invalid), the app SHALL present a neutral, human-readable
state (for example "your session expired — signing you back in") and route the
user to re-authentication, rather than rendering the transport-level error text.

**Forced-logout cleanup parity**: an involuntary logout triggered by an
unrecoverable `Unauthenticated` SHALL clear session state the same way a
voluntary sign-out does — it SHALL publish the same signed-out signal so that
user-specific caches/stores self-clear. The involuntary and voluntary logout
paths SHALL NOT diverge in what they clean up (a forced logout MUST NOT leave
stale user data behind).

**Return-to preservation**: on an involuntary re-authentication, the app SHALL
preserve where the user was so that, after re-authenticating, the user returns to
the same location rather than a default landing page.

**Unauthenticated caller pass-through**: an `Unauthenticated` response for a
caller that has no session (guest / pre-authentication flows) SHALL NOT trigger a
silent refresh or a forced logout; the error SHALL propagate to the caller so the
flow can handle it locally.

**Cross-context note**: the single-flight guard is per browsing context (per
tab). Concurrent refreshes across separate tabs or a service-worker-reloaded page
remain possible; they are tolerated (Zitadel rotation causes the loser to simply
refresh again) and cross-tab leader election is out of scope for this change.

#### Scenario: Recoverable expiry is invisible
- **WHEN** an RPC returns `Unauthenticated` because the access token expired
- **AND** a silent refresh succeeds and the retried RPC succeeds
- **THEN** the user SHALL NOT see any error text for that RPC

#### Scenario: Unrecoverable expiry shows a neutral state, not the raw error
- **WHEN** an RPC returns `Unauthenticated` and silent refresh fails (refresh
  token expired/invalid)
- **THEN** the app SHALL NOT render the transport-level error string to the user
- **AND** the app SHALL present a neutral "session expired" state and route to
  re-authentication

#### Scenario: Forced logout clears user data like a voluntary sign-out
- **WHEN** an unrecoverable `Unauthenticated` forces a logout
- **THEN** the app SHALL publish the same signed-out signal a voluntary sign-out
  publishes
- **AND** user-specific caches/stores SHALL be cleared
- **AND** no stale user data SHALL remain after the forced logout

#### Scenario: User returns to where they were after involuntary re-auth
- **WHEN** the user is forced to re-authenticate mid-session from a specific
  location
- **AND** they complete re-authentication
- **THEN** the app SHALL return them to that location (not a default landing page)

#### Scenario: Guest 401 propagates without refresh or logout
- **WHEN** an RPC returns `Unauthenticated` for a caller with no established
  session (guest / onboarding)
- **THEN** the app SHALL NOT attempt a silent refresh
- **AND** the app SHALL NOT force a logout/redirect
- **AND** the error SHALL propagate to the caller

## Architecture

### Components

- **JWT Validator**: Validates tokens using `github.com/lestrrat-go/jwx/v2`
- **authn-go Middleware**: `connectrpc/authn-go` HTTP middleware for default-deny authentication at the HTTP layer
- **Claims Bridge Interceptor**: Connect-RPC interceptor that converts `authn.GetInfo(ctx)` to `auth.WithClaims(ctx)` for backward compatibility
- **Context Utilities**: Type-safe user ID propagation through request context

### Configuration

```yaml
JWT_ISSUER: https://zitadel.example.com
JWT_JWKS_REFRESH_INTERVAL: 15m
```

### Flow

```
                     ┌────────────────┐
                     │  Public Mux    │
                     │ (health check) │
                     └────────────────┘
                              ▲
┌─────────────┐      ┌───────┴────────┐      ┌──────────────────┐      ┌─────────────┐
│   Client    │─────▶│   Root Mux     │─────▶│ authn Middleware  │─────▶│   Handler   │
│ (w/ Bearer) │      │ (path routing) │      │ (JWT Validator)   │      │ (uses ctx)  │
└─────────────┘      └────────────────┘      └──────────────────┘      └─────────────┘
                                                      │
                                                      ▼
                                             ┌─────────────────┐
                                             │ ZITADEL JWKS    │
                                             │ (Public Keys)   │
                                             └─────────────────┘
```

1. Request arrives at root mux
2. Health check requests are routed to public mux (no auth required)
3. All other requests are routed through `authn-go` middleware
4. Middleware extracts bearer token and validates via JWT Validator
5. Token validated against JWKS public keys, claims extracted
6. Claims set via `authn.SetInfo(ctx)`, bridge interceptor converts to `auth.WithClaims(ctx)`
7. Handler accesses user ID from context for scoped operations

## Dependencies

- `github.com/lestrrat-go/jwx/v2` - JWT validation and JWKS handling
- `connectrpc.com/authn` - HTTP-level authentication middleware for Connect-RPC
- ZITADEL JWKS endpoint (HTTPS required in production)

## Testing

- Unit tests for AuthFunc (valid token, missing token, invalid token, malformed bearer)
- Unit tests for claims bridge interceptor (claims propagation, nil info, wrong type)
- Unit tests for JWT validator and context utilities
- Integration tests with mock JWKS endpoint
- E2E testing with Playwright MCP storageState (see e2e-auth-testing capability)
