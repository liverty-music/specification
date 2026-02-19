## Context

The backend currently uses an `auth.AuthInterceptor` (Connect-RPC interceptor) that operates in passive mode: if no `Authorization` header is present, the request passes through unauthenticated. Individual handlers call `auth.GetUserID(ctx)` and return `CodeUnauthenticated` if needed. This is error-prone because any handler that forgets the check becomes a security gap.

The frontend uses Aurelia 2 router with per-component `canLoad()` lifecycle hooks for route protection. Only 2 of 4 protected routes have guards, leaving `/dashboard` and `/onboarding/discover` unprotected.

The system uses Zitadel as the OIDC provider with JWT tokens validated against JWKS.

## Goals / Non-Goals

**Goals:**
- Default-deny authentication on all backend API endpoints using `connectrpc/authn-go` HTTP middleware
- Eliminate handler-level auth checks by enforcing authentication before the request reaches the Connect interceptor chain
- Global frontend route guard using Aurelia 2 `@lifecycleHooks()` with declarative route metadata
- Health check endpoint accessible without authentication for Kubernetes probes
- Playwright MCP testability with `storageState` for authenticated E2E tests

**Non-Goals:**
- Authorization (role-based access control) — this change is authentication only
- Changing the OIDC provider or token format
- Adding API-level public endpoint allowlist (all current API calls require auth)

## Decisions

### Decision 1: Use `connectrpc/authn-go` instead of Connect interceptor for auth enforcement

**Choice:** Replace `auth.AuthInterceptor` with `authn.NewMiddleware()` wrapping the Connect mux.

**Why:** `authn-go` operates at the HTTP layer, rejecting unauthenticated requests before they enter the Connect interceptor chain. This is more efficient (no interceptor overhead for invalid requests) and safer (default-deny eliminates the risk of handler-level check omissions).

**Alternative considered:** Modify the existing interceptor to default-deny with a procedure allowlist. Rejected because: the interceptor still runs inside the Connect stack, consuming resources for every request including unauthenticated ones. `authn-go` is the official Connect-RPC authentication solution.

**Implementation:**

> **Note**: Code snippets in this design document are simplified pseudocode for illustration. Actual implementation may use different error handling patterns (e.g., `fmt.Errorf` instead of `authn.Errorf`). See the backend implementation in PR #65 for exact code.

```go
authMiddleware := authn.NewMiddleware(func(ctx context.Context, req *http.Request) (any, error) {
    token, ok := authn.BearerToken(req)
    if !ok {
        return nil, fmt.Errorf("missing bearer token")
    }
    claims, err := jwtValidator.ValidateToken(ctx, token)
    if err != nil {
        return nil, fmt.Errorf("invalid token: %w", err)
    }
    return claims, nil
})

handler := authMiddleware.Wrap(mux)
```

Handlers retrieve claims via `authn.GetInfo(ctx)` and type-assert to `*auth.Claims`.

### Decision 2: Separate health check onto its own mux

**Choice:** Register the gRPC health check handler on a separate `http.ServeMux` that is NOT wrapped by `authn.Middleware`. Combine both muxes under a top-level router that dispatches by path prefix.

**Why:** Kubernetes liveness/readiness probes must reach the health endpoint without authentication. Placing the health handler outside the authn middleware boundary keeps the default-deny semantics clean while allowing probe access.

**Implementation:**

```go
// Protected mux — all RPC services
protectedMux := http.NewServeMux()
// ... register UserService, ArtistService, ConcertService handlers ...

// Public mux — health check only
publicMux := http.NewServeMux()
healthPath, healthHandler := grpchealth.NewHandler(healthChecker, handlerOpts...)
publicMux.Handle(healthPath, healthHandler)

// Combine: wrap only protected mux with authn
rootMux := http.NewServeMux()
rootMux.Handle(healthPath, publicMux)
rootMux.Handle("/", authMiddleware.Wrap(protectedMux))
```

### Decision 3: Remove `auth.AuthInterceptor`, retain `auth.Claims` and context helpers

**Choice:** Delete `AuthInterceptor` and its tests. Keep `Claims` struct, `WithClaims()`, `GetClaims()`, `GetUserID()` context helpers. Add a thin adapter in the `AuthFunc` that calls `WithClaims()` so downstream code continues to use the existing context API.

**Why:** The `Claims` type and context helpers are used by every handler. Changing all handlers to use `authn.GetInfo()` with type assertions adds risk and churn for no benefit. The `AuthFunc` bridges `authn-go` → existing context pattern seamlessly.

**Alternative considered:** Replace all `auth.GetUserID()` calls with `authn.GetInfo()`. Rejected: high churn, no safety benefit, and couples handlers to the `authn-go` API directly.

**Note:** Since `authn.SetInfo` happens inside the middleware `Wrap` method (not accessible to us), we need to set claims on the context within the `AuthFunc`. However, `authn-go`'s `AuthFunc` returns `(any, error)` and the middleware sets the returned value via `SetInfo`. So downstream code should use `authn.GetInfo(ctx).(*auth.Claims)`. To preserve backward compatibility, we add a Connect interceptor that reads `authn.GetInfo` and calls `auth.WithClaims`:

```go
// Bridge interceptor: authn.GetInfo → auth.WithClaims
func claimsBridgeInterceptor() connect.UnaryInterceptorFunc {
    return func(next connect.UnaryFunc) connect.UnaryFunc {
        return func(ctx context.Context, req connect.AnyRequest) (connect.AnyResponse, error) {
            if info := authn.GetInfo(ctx); info != nil {
                if claims, ok := info.(*auth.Claims); ok {
                    ctx = auth.WithClaims(ctx, claims)
                }
            }
            return next(ctx, req)
        }
    }
}
```

This replaces the old `AuthInterceptor` in the interceptor chain, is much simpler, and preserves all existing handler code.

### Decision 4: Frontend global auth guard via `@lifecycleHooks()` with route `data` metadata

**Choice:** Create a single `AuthHook` class decorated with `@lifecycleHooks()` that implements `canLoad`. All routes are protected by default (default-deny). Public routes explicitly declare `data: { auth: false }` in their route configuration to opt out. The hook checks `IAuthService.isAuthenticated` and redirects to the landing page with a toast notification if the user is not authenticated.

**Why:** Default-deny eliminates the risk of accidentally exposing a new route without authentication. Only routes that are explicitly public need annotation, which is a safer default than requiring every protected route to opt in.

**Alternative considered:** Protected routes declare `data: { auth: AuthHook }` to opt in. Rejected: new routes would be unprotected by default, creating a risk of forgetting to add the annotation.

### Decision 5: Playwright MCP testing via `storageState`

**Choice:** Use Playwright MCP's `--isolated --storage-state` flag to inject a pre-captured authenticated session into the browser context.

**Why:** This is the official Playwright MCP approach. The storageState file contains cookies and localStorage including OIDC tokens. The `offline_access` scope ensures refresh tokens are available for longer session validity.

**Workflow:**
1. One-time setup: Run a Playwright script that logs into Zitadel with a test user, captures `storageState.json`
2. MCP config: `--isolated --storage-state=.auth/storageState.json`
3. All MCP browser sessions start authenticated, API calls include valid Bearer tokens

## Risks / Trade-offs

**[Risk] Handler-level `auth.GetUserID()` checks become redundant** → These checks are now defense-in-depth rather than primary protection. They can remain as-is (no immediate removal needed) since they provide an extra safety layer and return clear error messages. Removal is a future cleanup task.

**[Risk] `storageState.json` tokens expire** → Mitigated by `offline_access` scope providing refresh tokens. `oidc-client-ts` handles automatic token refresh in the browser context. For CI, a pre-test setup step regenerates the storageState.

**[Risk] New dependency `connectrpc.com/authn`** → The library is maintained by the Connect-RPC team, follows semantic versioning, and is the official auth solution for Connect. Low risk.

**[Risk] Health check path routing correctness** → The separate mux approach requires exact path matching. Validated by existing health check tests and K8s probe configuration.
