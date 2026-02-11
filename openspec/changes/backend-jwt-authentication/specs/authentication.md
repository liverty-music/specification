# Authentication Capability (Delta Spec)

## Overview
JWT-based authentication for user-specific operations in the backend.

## Requirements

### Functional Requirements
- **FR-1**: Validate JWT tokens from ZITADEL using JWKS endpoint
- **FR-2**: Extract user ID from validated token's `sub` claim
- **FR-3**: Propagate user ID through request context
- **FR-4**: Require authentication for Follow/Unfollow/ListFollowed operations
- **FR-5**: Allow public access to Search/ListTop/ListSimilar operations

### Non-Functional Requirements
- **NFR-1**: JWKS keys must be cached and auto-refreshed (default: 15 minutes)
- **NFR-2**: Token validation must complete within 100ms
- **NFR-3**: Failed authentication must return `connect.CodeUnauthenticated`

## Architecture

### Components
- **JWT Validator**: Validates tokens using `github.com/lestrrat-go/jwx/v2`
- **Auth Interceptor**: Connect-RPC middleware for token extraction and validation
- **Context Utilities**: Type-safe user ID propagation

### Configuration
```yaml
JWT_ISSUER: https://zitadel.example.com
JWKS_REFRESH_INTERVAL: 15m
```

## Dependencies
- `github.com/lestrrat-go/jwx/v2` - JWT validation and JWKS handling

## Testing
- Unit tests for validator, interceptor, and context utilities
- Integration tests with mock JWKS endpoint
- Manual testing with real ZITADEL tokens
