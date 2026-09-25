## Context

The admin Connect server (`internal/di/provider.go`) is built with `server.NewConnectServer(adminServerCfg, logger, authFunc, ..., adminInterceptors, ..., adminHandlers...)`, reusing the exact same `authFunc` instance the consumer (fan) server uses. `authFunc` is `auth.NewAuthFunc(jwtValidator, publicProcedures)`, and `publicProcedures` lists `/ArtistService/ListTop`, `/ArtistService/ListSimilar` and `/ArtistService/Search` as public so the fan boundary can serve them without sign-in. Because the admin server also mounts the consumer `ArtistService` handler (so the admin console can reuse `Search` to pick an artist to associate with an organizer — see `components/adapter/admin/api/rpc/artist`), the procedure names collide: `authn.InferProcedure` sees the same `/ArtistService/ListTop` path regardless of which server received the request, so the shared allowlist makes these three procedures public on the admin server too. An unauthenticated request to them reaches the handler with no claims in context instead of being rejected by the authn middleware.

Once such a request reaches `auth.RequireRoleInterceptor` (the admin server's sole authorization gate, applied server-wide), `auth.RequireRole` calls `GetClaims` and, finding none, returns `connect.CodePermissionDenied` — the same code used when claims are present but the role is missing. This is the second half of the bug: even without the allowlist collision, `RequireRole`'s own "no claims" branch is mis-coded as PermissionDenied instead of Unauthenticated, so it silently produces the wrong code for any procedure that ever reaches it unauthenticated (belt-and-suspenders fix, see Decisions).

## Goals / Non-Goals

**Goals:**
- No procedure on the admin server is ever treated as public, regardless of what the consumer server's allowlist contains, now or in the future (structural fix, not a three-method special case).
- `RequireRole` reports the documented contract on its own: Unauthenticated when the caller has no claims, PermissionDenied when the caller has claims but lacks the role.

**Non-Goals:**
- Changing which procedures are public on the fan/consumer server — `ListTop`, `ListSimilar` and `Search` stay public there.
- Changing the RPC surface, request/response shapes, or the `ArtistService` handler itself.

## Decisions

### Give the admin server its own `authn.AuthFunc` with no public procedures

**Choice**: In `internal/di/provider.go`, construct a second `auth.NewAuthFunc(jwtValidator, nil)` (empty/nil allowlist) for the admin server instead of passing it the consumer server's `authFunc`. Both `AuthFunc`s share the same `jwtValidator`, so token validation behavior (issuer, JWKS, accepted issuers) is identical; only the public-procedure allowlist differs. This makes "the admin surface has no public procedures" a structural property of the admin server's wiring, matching the existing comment that the admin server's authorization is meant to be "impossible to register an un-gated admin RPC" — the same guarantee now extends to authentication, not just role authorization.

**Alternatives considered**:
- Namespace `publicProcedures` keys by server (e.g. prefix with `fan:`/`admin:`) and pass the same map to both: more invasive (touches every existing key and both `NewAuthFunc` call sites) for the same outcome, and leaves a shared mutable map that both servers read, inviting future accidental additions to leak across servers again.
- Remove the consumer `ArtistService.ListTop`/`ListSimilar`/`Search` public entries and require sign-in fan-side too: rejected — that would change the fan-facing (already correct, and intentionally public) contract, which is out of scope and a product decision, not a bug fix.

### Also fix `RequireRole`'s "no claims" branch to return Unauthenticated

**Choice**: In `internal/infrastructure/auth/context.go`, `RequireRole` returns `connect.CodeUnauthenticated` (not `CodePermissionDenied`) when `GetClaims` finds no claims, keeping `CodePermissionDenied` for the "claims present, role missing" branch. This is defense in depth: `RequireRoleInterceptor` is documented as "the sole, structural authorization gate" for the admin server, so it should report the correct code on its own even if some future public-procedure allowlist change again lets an unauthenticated request reach it. It also corrects the doc comment on `RequireRole`, which currently documents the buggy behavior.

**Alternatives considered**:
- Rely solely on the allowlist fix above and leave `RequireRole` as is: works for today's admin surface (the authn middleware now always rejects an unauthenticated caller before the interceptor runs), but leaves a latent trap — a future admin procedure accidentally added to a public-procedure allowlist would resurface exactly this bug with no test catching the interceptor's own contract.

## Risks / Trade-offs

- [Risk] A future admin handler might be registered only in `adminHandlers` and forgotten from `authFunc`'s new empty allowlist assumption — i.e., someone could still add an entry to the *admin* `authFunc`'s allowlist by mistake. → Mitigation: the admin `AuthFunc` is constructed with a `nil` map at a single call site with a comment explaining why it must stay empty; the new table test in `internal/infrastructure/server` (or `internal/di`) asserts every registered admin procedure requires auth, catching a regression immediately.
- [Risk] Divergent `AuthFunc` instances for admin vs. consumer could drift in token-validation behavior if someone edits one but not the other. → Mitigation: both are built from the same `jwtValidator` variable; only the allowlist argument differs, and that is now `nil` by design for admin.

## Migration Plan

No data migration. This is a pure authorization-code-path fix, deployed as a normal backend release; no client changes required (`ListTop`/`ListSimilar`/`Search` remain public on the fan boundary, which is what clients use).
