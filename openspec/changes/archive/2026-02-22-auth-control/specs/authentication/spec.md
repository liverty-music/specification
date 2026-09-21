# Authentication (Delta)

## REMOVED Requirements

### Requirement: Auth Interceptor

**Reason**: Replaced by `connectrpc/authn-go` HTTP middleware. The `auth.AuthInterceptor` Connect-RPC interceptor is no longer needed because authentication is enforced at the HTTP layer before the interceptor chain.

**Migration**: Remove `auth.AuthInterceptor` and its tests. The `AuthFunc` in `authn-go` uses the existing `TokenValidator` interface. A thin bridge interceptor converts `authn.GetInfo(ctx)` to `auth.WithClaims(ctx)` for backward compatibility with handler code.
