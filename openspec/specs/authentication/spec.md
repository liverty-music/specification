# Authentication Capability

## Purpose

JWT-based authentication for user-specific operations in the backend. This capability validates JWT tokens from ZITADEL using their JWKS endpoint to authenticate API requests and scope operations to individual users.

## Requirements

### Functional Requirements

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

**Rationale**: Zitadel does not include `email_verified` in access tokens by default. The backend requires this claim to enforce email verification at the API layer.

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

### Requirement: Backend Email Verification Enforcement

The system SHALL reject authenticated requests where the access token's `email_verified` claim is not `true`, returning `connect.CodeUnauthenticated`.

**Rationale**: Defense-in-depth. Even though Zitadel's Hosted Login enforces email verification when SMTP is configured, the backend SHALL independently verify the claim to guard against API-created users or misconfigured identity providers.

#### Scenario: Request with verified email

- **WHEN** an authenticated request includes a valid JWT with `email_verified: true`
- **THEN** the system SHALL allow the request to proceed to the RPC handler
- **AND** the `EmailVerified` field SHALL be available in `Claims`

#### Scenario: Request with unverified email

- **WHEN** an authenticated request includes a valid JWT with `email_verified: false`
- **THEN** the system SHALL reject the request with `connect.CodeUnauthenticated`
- **AND** the error message SHALL indicate that email verification is required

#### Scenario: Request with missing email_verified claim

- **WHEN** an authenticated request includes a valid JWT without the `email_verified` claim
- **THEN** the system SHALL reject the request with `connect.CodeUnauthenticated`
- **AND** the error message SHALL indicate that email verification is required

#### Scenario: Machine user token without email_verified

- **WHEN** an authenticated request uses a machine user token (no `email_verified` claim, no `email` claim)
- **THEN** the system SHALL allow the request if it passes existing validation
- **AND** the `email_verified` check SHALL be skipped for tokens without an `email` claim

### Requirement: Frontend Email Verification Check

The system SHALL verify the user's `email_verified` status during the OIDC callback and display an error if the email is not verified.

**Rationale**: Immediate user feedback. Rather than letting the user reach the dashboard and fail on every API call, the frontend SHALL catch unverified emails at the earliest opportunity and guide the user.

#### Scenario: Callback with verified email

- **WHEN** the OIDC callback processes a token where `email_verified` is `true` in the ID token profile
- **THEN** the system SHALL proceed with normal flow (provisioning, merge, redirect to dashboard)

#### Scenario: Callback with unverified email

- **WHEN** the OIDC callback processes a token where `email_verified` is `false` or missing in the ID token profile
- **THEN** the system SHALL NOT proceed to user provisioning or guest data merge
- **AND** the system SHALL display an error message instructing the user to verify their email
- **AND** the system SHALL provide a way to return to the login flow

### Non-Functional Requirements

### Requirement: JWKS Caching

The system SHALL cache JWKS keys and auto-refresh them periodically.

**Rationale**: Fetching public keys on every request would add unacceptable latency. Caching with periodic refresh balances security (key rotation) with performance.

**Acceptance Criteria**:
- Default refresh interval: 15 minutes
- Configurable via `JWT_JWKS_REFRESH_INTERVAL` environment variable
- Initial fetch on startup with validation before server accepts requests

### Requirement: Token Validation Performance

The system SHALL complete token validation within 100ms under normal conditions.

**Rationale**: Authentication adds overhead to every authenticated request. Keeping validation fast ensures acceptable API response times.

**Acceptance Criteria**:
- P95 latency for token validation: < 100ms
- Uses efficient JWT parsing library (`github.com/lestrrat-go/jwx/v2`)
- JWKS cache minimizes network calls

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

## Architecture

### Components

- **JWT Validator**: Validates tokens using `github.com/lestrrat-go/jwx/v2`
- **authn-go Middleware**: `connectrpc/authn-go` HTTP middleware for default-deny authentication at the HTTP layer
- **Claims Bridge Interceptor**: Connect-RPC interceptor that converts `authn.GetInfo(ctx)` to `auth.WithClaims(ctx)` for backward compatibility
- **Email Verification Interceptor**: Connect-RPC interceptor that enforces `email_verified` claim for human users, skipping machine users and public endpoints
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
