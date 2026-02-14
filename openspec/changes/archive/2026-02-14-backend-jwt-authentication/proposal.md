# Proposal: Backend JWT Authentication

## Problem Statement

Currently, the backend does not validate JWT tokens from ZITADEL, meaning user-specific operations (Follow/Unfollow/ListFollowed) cannot be properly authenticated or scoped to individual users.

## Proposed Solution

Implement JWT token validation using ZITADEL's JWKS endpoint with the following components:

1. **JWT Validator**: Use `github.com/lestrrat-go/jwx/v2` to validate tokens against ZITADEL's public keys
2. **Connect-RPC Interceptor**: Extract and validate Bearer tokens from request headers
3. **Context Utilities**: Propagate authenticated user ID through request context
4. **Handler Updates**: Modify Follow/Unfollow/ListFollowed to require authentication

## Benefits

- **Security**: Only authenticated users can perform user-specific operations
- **User Scoping**: Operations are correctly scoped to the authenticated user
- **Standards Compliance**: Uses industry-standard JWT validation with JWKS
- **Flexibility**: Public endpoints (Search, ListTop) remain accessible without authentication

## Alternatives Considered

1. **ZITADEL Go SDK**: More heavyweight, includes unnecessary features for our use case
2. **Custom JWT parsing**: Reinventing the wheel, error-prone
3. **No authentication**: Security risk, cannot scope operations to users

## Decision

Proceed with `jwx/v2` for its robustness, lightweight design, and excellent JWKS support.
