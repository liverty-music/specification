<!-- Extracted 2026-09-21 from openspec/specs/authentication/spec.md lines 359-416.
     Non-product sections removed so the spec has only Purpose and Requirements.
     Sections: Architecture, Dependencies, Testing
     Routed in Phase 1 manifest (OUT:design-doc / OUT:delete). -->

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
