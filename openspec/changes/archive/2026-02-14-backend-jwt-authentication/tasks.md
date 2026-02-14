## 1. Configuration & Dependencies

- [x] 1.1 Add JWT library dependency (`github.com/lestrrat-go/jwx/v2`) to go.mod
- [x] 1.2 Add JWT configuration fields to `pkg/config/config.go`
    - [x] `JWTIssuer` field
    - [x] `JWKSRefreshInterval` field
- [x] 1.3 Add environment variable documentation to Config struct
- [x] 1.4 Add JWT config validation in `config.Validate()`

## 2. Context Utilities

- [x] 2.1 Create `internal/infrastructure/auth/context.go`
    - [x] Define type-safe context key
    - [x] Implement `WithUserID(ctx, userID)` function
    - [x] Implement `GetUserID(ctx)` function
- [x] 2.2 Write unit tests for context utilities

## 3. JWT Validator

- [x] 3.1 Create `internal/infrastructure/auth/jwt_validator.go`
    - [x] Define `JWTValidator` struct with JWKS cache
    - [x] Implement `NewJWTValidator(issuer, jwksURL, refreshInterval)` constructor
    - [x] Implement `ValidateToken(tokenString)` method
- [x] 3.2 Write unit tests for JWT validator

## 4. Auth Interceptor

- [x] 4.1 Create `internal/infrastructure/auth/interceptor.go`
    - [x] Implement `NewAuthInterceptor(validator)` function
    - [x] Extract Bearer token from Authorization header
    - [x] Call validator and populate context with user ID
    - [x] Return appropriate error codes for auth failures
- [x] 4.2 Write unit tests for interceptor

## 5. Server Integration

- [x] 5.1 Update `internal/infrastructure/server/connect.go`
    - [x] Accept auth interceptor in `NewConnectServer`
    - [x] Register interceptor in middleware chain
- [x] 5.2 Update `internal/di/provider.go`
    - [x] Wire up JWT validator
    - [x] Wire up auth interceptor
    - [x] Pass to Connect server

## 6. Handler Updates

- [~] 6.1 Update `internal/adapter/rpc/artist_handler.go` - **SKIPPED**: Artist service not in current buf schema
- [~] 6.2 Update handler tests to mock authenticated context - **SKIPPED**: Depends on 6.1

## 7. Verification

- [x] 7.1 Run all unit tests: `go test ./...` - Core tests pass (JWT validation, context utilities, config)
- [~] 7.2 Manual test: Start server and verify JWKS initialization in logs - **MOVED**: See issue #42
- [~] 7.3 Manual test: Call Follow without token, verify `CodeUnauthenticated` - **MOVED**: See issue #42
- [~] 7.4 Manual test: Call ListTop without token, verify it works (public endpoint) - **MOVED**: See issue #42
- [~] 7.5 Manual test: Call Follow with valid token, verify success - **MOVED**: See issue #42
