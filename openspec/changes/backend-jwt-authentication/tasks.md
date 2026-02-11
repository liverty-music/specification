## 1. Configuration & Dependencies

- [ ] 1.1 Add JWT library dependency (`github.com/lestrrat-go/jwx/v2`) to go.mod
- [ ] 1.2 Add JWT configuration fields to `pkg/config/config.go`
    - [ ] `JWTIssuer` field
    - [ ] `JWKSRefreshInterval` field
- [ ] 1.3 Add environment variable documentation to Config struct
- [ ] 1.4 Add JWT config validation in `config.Validate()`

## 2. Context Utilities

- [ ] 2.1 Create `internal/infrastructure/auth/context.go`
    - [ ] Define type-safe context key
    - [ ] Implement `WithUserID(ctx, userID)` function
    - [ ] Implement `GetUserID(ctx)` function
- [ ] 2.2 Write unit tests for context utilities

## 3. JWT Validator

- [ ] 3.1 Create `internal/infrastructure/auth/jwt_validator.go`
    - [ ] Define `JWTValidator` struct with JWKS cache
    - [ ] Implement `NewJWTValidator(issuer, jwksURL, refreshInterval)` constructor
    - [ ] Implement `ValidateToken(tokenString)` method
- [ ] 3.2 Write unit tests for JWT validator

## 4. Auth Interceptor

- [ ] 4.1 Create `internal/infrastructure/auth/interceptor.go`
    - [ ] Implement `NewAuthInterceptor(validator)` function
    - [ ] Extract Bearer token from Authorization header
    - [ ] Call validator and populate context with user ID
    - [ ] Return appropriate error codes for auth failures
- [ ] 4.2 Write unit tests for interceptor

## 5. Server Integration

- [ ] 5.1 Update `internal/infrastructure/server/connect.go`
    - [ ] Accept auth interceptor in `NewConnectServer`
    - [ ] Register interceptor in middleware chain
- [ ] 5.2 Update `internal/di/provider.go`
    - [ ] Wire up JWT validator
    - [ ] Wire up auth interceptor
    - [ ] Pass to Connect server

## 6. Handler Updates

- [ ] 6.1 Update `internal/adapter/rpc/artist_handler.go`
    - [ ] Modify `Follow` to extract user ID from context
    - [ ] Modify `Unfollow` to extract user ID from context
    - [ ] Modify `ListFollowed` to extract user ID from context
    - [ ] Return `CodeUnauthenticated` if user ID is missing
- [ ] 6.2 Update handler tests to mock authenticated context

## 7. Verification

- [ ] 7.1 Run all unit tests: `go test ./...`
- [ ] 7.2 Manual test: Start server and verify JWKS initialization in logs
- [ ] 7.3 Manual test: Call Follow without token, verify `CodeUnauthenticated`
- [ ] 7.4 Manual test: Call ListTop without token, verify it works (public endpoint)
- [ ] 7.5 Manual test: Call Follow with valid token, verify success
