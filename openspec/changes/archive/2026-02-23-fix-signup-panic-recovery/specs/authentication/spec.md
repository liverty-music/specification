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

#### Scenario: Claims bridge interceptor position in chain

- **WHEN** the Connect interceptor chain processes a request
- **THEN** the `ClaimsBridgeInterceptor` SHALL run after the panic recovery interceptor and before the validation interceptor
- **AND** the `ClaimsBridgeInterceptor` SHALL have access to OTel trace context in its `ctx` argument
