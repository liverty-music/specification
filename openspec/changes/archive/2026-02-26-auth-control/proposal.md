## Why

The current system specifies that all views beyond the landing page require authentication, but neither the frontend nor the backend enforce this. Users can navigate directly to protected routes (e.g., `/dashboard`, `/onboarding/discover`) without signing in, and the backend API accepts unauthenticated requests on endpoints that should be protected. This creates a security gap where user-specific data and actions are accessible without identity verification.

## What Changes

- **BREAKING**: Backend switches from passive auth interceptor (validate-if-present) to `connectrpc/authn-go` middleware with default-deny semantics. All RPC requests require a valid JWT unless the endpoint is explicitly public.
- **BREAKING**: Backend health check endpoint moves to a separate `http.ServeMux` outside the authn middleware, ensuring Kubernetes probes are unaffected.
- Remove the existing `auth.Interceptor` and consolidate JWT validation + claims injection into the `authn-go` `AuthFunc`.
- Frontend adds a global Aurelia 2 `@lifecycleHooks()` auth guard that protects routes declaratively via route `data` metadata. No more per-component `canLoad` guards scattered across files.
- Frontend uses default-deny route protection: all routes require authentication unless explicitly marked with `data: { auth: false }`. Public routes (`/`, `/about`, `/auth/callback`) declare this opt-out.
- Configure Playwright MCP with `--isolated --storage-state` for authenticated E2E testing against the enforced auth layer.

## Capabilities

### New Capabilities

- `frontend-route-guard`: Global authentication guard for frontend routing using Aurelia 2 lifecycle hooks. Redirects unauthenticated users to the landing page for protected routes.
- `e2e-auth-testing`: Playwright MCP configuration for running automated E2E tests against authenticated routes using pre-captured storageState.

### Modified Capabilities

- `authentication`: Backend auth enforcement changes from passive interceptor to `connectrpc/authn-go` HTTP middleware with default-deny. Health check moves to a separate mux.

## Impact

- **Backend (`backend/`)**: `internal/infrastructure/auth/` (interceptor removal, authn-go integration), `internal/infrastructure/server/connect.go` (server setup, health check separation), `go.mod` (new dependency: `connectrpc.com/authn`)
- **Frontend (`frontend/`)**: `src/my-app.ts` (route definitions with `data` metadata), new `src/hooks/auth-hook.ts`, removal of per-component `canLoad` guards
- **Testing**: New `.auth/storageState.json` for Playwright MCP, MCP config update
- **Specification**: `openspec/specs/authentication/spec.md` (delta for default-deny)
