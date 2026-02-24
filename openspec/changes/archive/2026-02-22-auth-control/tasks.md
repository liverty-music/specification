## 1. Backend: authn-go Integration

- [x] 1.1 Add `connectrpc.com/authn` dependency to `go.mod`
- [x] 1.2 Create `AuthFunc` in `internal/infrastructure/auth/` that uses `authn.BearerToken()` and the existing `TokenValidator` to validate tokens and return `*Claims`
- [x] 1.3 Create bridge interceptor that converts `authn.GetInfo(ctx)` to `auth.WithClaims(ctx)` for backward compatibility with handler code
- [x] 1.4 Write unit tests for `AuthFunc` (valid token, missing token, invalid token, malformed bearer)
- [x] 1.5 Write unit tests for the bridge interceptor (claims propagation, nil info passthrough)

## 2. Backend: Server Restructure

- [x] 2.1 Refactor `NewConnectServer` to separate health check handler onto its own `http.ServeMux` outside the authn middleware boundary
- [x] 2.2 Create `authn.NewMiddleware` wrapping the protected mux with the `AuthFunc`
- [x] 2.3 Combine public mux (health) and protected mux (all RPC services) under a root mux with path-based dispatch
- [x] 2.4 Remove `auth.AuthInterceptor` from the Connect interceptor chain, replace with the bridge interceptor
- [x] 2.5 Update DI provider to wire `authn.Middleware` instead of `AuthInterceptor`

## 3. Backend: Cleanup

- [x] 3.1 Delete `auth.AuthInterceptor` struct and its `WrapUnary`/`WrapStreamingHandler` methods
- [x] 3.2 Delete `interceptor_test.go` (old interceptor tests)
- [x] 3.3 Verify all existing handler tests pass (handlers still use `auth.GetUserID(ctx)` unchanged)
- [x] 3.4 Run linter and fix any issues

## 4. Frontend: Global Auth Hook

- [x] 4.1 Create `src/hooks/auth-hook.ts` with `@lifecycleHooks()` decorator implementing `canLoad` that checks `IAuthService.isAuthenticated` and redirects to `/`
- [x] 4.2 Ensure the auth hook awaits `authService.ready` before evaluating auth state
- [x] 4.3 Add `data: { auth: false }` to public route definitions in `my-app.ts` (`/`, `/about`, `/auth/callback`); protected routes require no annotation (default-deny)
- [x] 4.4 Remove per-component `canLoad` auth checks from `loading-sequence.ts` and `welcome-page.ts` (keep only non-auth routing logic like onboarding status checks)

## 5. E2E Auth Testing Setup

- [x] 5.1 Create `.auth/` directory and add `.auth/` to `.gitignore` in the frontend project
- [x] 5.2 Create storageState capture script (`scripts/capture-auth-state.ts`) that logs in with a test user and saves browser state
- [x] 5.3 Update MCP configuration to use `--isolated --storage-state=.auth/storageState.json`
- [x] 5.4 Verify Playwright MCP can navigate protected routes with the captured storageState
