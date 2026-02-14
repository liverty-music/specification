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

#### Scenario: Invalid Token

- **WHEN** a request includes an invalid or expired JWT token
- **THEN** the system rejects the request with `connect.CodeUnauthenticated`
- **AND** logs the authentication failure for security monitoring

### Requirement: User ID Propagation

The system SHALL extract the user ID from validated tokens and propagate it through the request context.

**Rationale**: Handlers need access to the authenticated user ID to scope operations correctly (e.g., following artists, viewing followed content).

#### Scenario: Authenticated Request

- **WHEN** a JWT token is successfully validated
- **THEN** the system extracts the user ID from the token's `sub` claim
- **AND** adds the user ID to the request context
- **AND** makes the user ID accessible to downstream handlers

### Requirement: Authenticated Endpoint Protection

The system SHALL require authentication for user-specific operations (Follow/Unfollow/ListFollowed).

**Rationale**: User-specific operations must be scoped to the authenticated user to prevent unauthorized access to other users' data.

#### Scenario: Follow Artist Without Token

- **WHEN** a request to follow an artist does not include an Authorization header
- **THEN** the system returns `connect.CodeUnauthenticated`
- **AND** does not execute the follow operation

#### Scenario: Follow Artist With Valid Token

- **WHEN** a request to follow an artist includes a valid JWT token
- **THEN** the system validates the token
- **AND** extracts the user ID from the token
- **AND** executes the follow operation scoped to that user ID

### Requirement: Public Endpoint Access

The system SHALL allow public access to Search/ListTop/ListSimilar operations without authentication.

**Rationale**: Discovery and browsing features should be accessible to all users, including unauthenticated visitors, to encourage platform adoption.

#### Scenario: Search Without Token

- **WHEN** a request to search for artists does not include an Authorization header
- **THEN** the system processes the request successfully
- **AND** returns search results without requiring authentication

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
- **Auth Interceptor**: Connect-RPC middleware for token extraction and validation
- **Context Utilities**: Type-safe user ID propagation through request context

### Configuration

```yaml
JWT_ISSUER: https://zitadel.example.com
JWT_JWKS_REFRESH_INTERVAL: 15m
```

### Flow

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│   Client    │─────▶│ Auth Interceptor │─────▶│   Handler   │
│ (w/ Bearer) │      │  (JWT Validator) │      │ (uses ctx)  │
└─────────────┘      └──────────────────┘      └─────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ ZITADEL JWKS    │
                     │ (Public Keys)   │
                     └─────────────────┘
```

1. Request arrives with `Authorization: Bearer <token>` header
2. Interceptor extracts token from header
3. Validator fetches JWKS from ZITADEL (cached with refresh)
4. Token validated against public keys, claims verified
5. User ID extracted from `sub` claim
6. Context populated with authenticated user ID
7. Handler accesses user ID from context for scoped operations

## Dependencies

- `github.com/lestrrat-go/jwx/v2` - JWT validation and JWKS handling
- ZITADEL JWKS endpoint (HTTPS required in production)

## Testing

- Unit tests for validator, interceptor, and context utilities
- Integration tests with mock JWKS endpoint
- Manual testing with real ZITADEL tokens
