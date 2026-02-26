# Authentication (Delta)

## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: Auth Interceptor

**Reason**: Replaced by `connectrpc/authn-go` HTTP middleware. The `auth.AuthInterceptor` Connect-RPC interceptor is no longer needed because authentication is enforced at the HTTP layer before the interceptor chain.

**Migration**: Remove `auth.AuthInterceptor` and its tests. The `AuthFunc` in `authn-go` uses the existing `TokenValidator` interface. A thin bridge interceptor converts `authn.GetInfo(ctx)` to `auth.WithClaims(ctx)` for backward compatibility with handler code.
