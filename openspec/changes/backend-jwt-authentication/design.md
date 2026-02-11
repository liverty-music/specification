# Design: Backend JWT Authentication

## Context

The backend needs to authenticate users for personalized operations (following artists, viewing followed artists). ZITADEL provides JWT tokens with user identity claims that must be validated using their JWKS endpoint.

## Architecture

### Components

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

### Flow

1. **Request arrives** with `Authorization: Bearer <token>` header
2. **Interceptor extracts** token from header
3. **Validator fetches** JWKS from ZITADEL (cached with refresh)
4. **Token validated** against public keys, claims verified
5. **User ID extracted** from `sub` claim
6. **Context populated** with authenticated user ID
7. **Handler accesses** user ID from context for scoped operations

## Implementation Details

### JWT Validator (`internal/infrastructure/auth/jwt_validator.go`)

```go
type JWTValidator struct {
    jwks      *jwk.Cache
    issuer    string
}

func (v *JWTValidator) ValidateToken(tokenString string) (string, error)
```

- Uses `jwk.NewCache()` with auto-refresh
- Validates issuer, expiration, and signature
- Returns user ID from `sub` claim

### Auth Interceptor (`internal/infrastructure/auth/interceptor.go`)

```go
func NewAuthInterceptor(validator *JWTValidator) connectgo.UnaryInterceptorFunc
```

- Extracts Bearer token from `Authorization` header
- Calls validator to verify token
- Populates context with user ID using `WithUserID()`
- Returns `connect.CodeUnauthenticated` on failure

### Context Utilities (`internal/infrastructure/auth/context.go`)

```go
func WithUserID(ctx context.Context, userID string) context.Context
func GetUserID(ctx context.Context) (string, bool)
```

- Type-safe context key for user ID
- Accessor functions for setting/getting user ID

### Configuration

```go
type Config struct {
    JWTIssuer            string        `envconfig:"JWT_ISSUER"`
    JWKSRefreshInterval  time.Duration `envconfig:"JWKS_REFRESH_INTERVAL" default:"15m"`
}
```

## Security Considerations

- **Token expiration**: Validated automatically by `jwx/v2`
- **Signature verification**: Uses ZITADEL's public keys from JWKS
- **Issuer validation**: Ensures tokens are from configured ZITADEL instance
- **HTTPS required**: JWKS endpoint must use HTTPS in production

## Public vs. Authenticated Endpoints

### Public (No Auth Required)
- `ArtistService.List`
- `ArtistService.Search`
- `ArtistService.ListTop`
- `ArtistService.ListSimilar`
- `ConcertService.*` (all endpoints)

### Authenticated (Requires JWT)
- `ArtistService.Follow`
- `ArtistService.Unfollow`
- `ArtistService.ListFollowed`

## Error Handling

- **Missing token**: Return `connect.CodeUnauthenticated` with message "missing authorization header"
- **Invalid token**: Return `connect.CodeUnauthenticated` with message "invalid token"
- **Expired token**: Return `connect.CodeUnauthenticated` with message "token expired"
- **JWKS fetch failure**: Log error, return `connect.CodeInternal`

## Testing Strategy

1. **Unit tests**: Mock validator, test interceptor logic
2. **Integration tests**: Use test JWKS endpoint with known keys
3. **Manual testing**: Use real ZITADEL tokens in dev environment
