## Why

Every admin-console RPC is meant to reject an unauthenticated caller with Unauthenticated and a signed-in non-admin caller with PermissionDenied (this is already the documented and shipped behavior for Concert, Organizer and Order). ArtistService's `ListTop`, `ListSimilar` and `Search` are the exception: on the admin server they currently return PermissionDenied for an unauthenticated caller too, because the admin server shares the fan server's `publicProcedures` allowlist (these three methods are intentionally public on the fan boundary) and the interceptor's own claims check also collapses "no claims" into PermissionDenied. The `components/adapter/admin/api/rpc/artist` spec currently documents this quirk as intended ("Guest browses ... fails with PermissionDenied") instead of the correct, uniform contract.

## What Changes

- The admin artist requirement is corrected to match every other admin RPC boundary: an unauthenticated caller SHALL fail with Unauthenticated, and a signed-in caller without the admin role SHALL fail with PermissionDenied, for every artist call reached through the admin console — including `ListTop`, `ListSimilar` and `Search`, which stay public only on the fan boundary.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `components/adapter/admin/api/rpc/artist`: the "Every artist call on the admin console needs the admin role" requirement is corrected so an unauthenticated caller always fails with Unauthenticated (previously the "Guest browses" scenario documented PermissionDenied for `ListTop`/`ListSimilar`/`Search`, matching a bug in the admin server's shared public-procedure allowlist and role-check interceptor).

## Impact

- **Backend**: `internal/di/provider.go` (the admin Connect server must not share the fan server's `publicProcedures` allowlist — no admin procedure is ever public), `internal/infrastructure/auth/context.go` (`RequireRole` must return Unauthenticated when no claims are present, PermissionDenied only when claims are present but the role is missing), plus their tests (`internal/infrastructure/auth/authz_test.go`, `internal/infrastructure/auth/context_test.go`) and a new table test over the admin server's RPC procedures.
- **No proto/RPC changes**: the RPC surface and its inputs/outputs are unchanged; only the error code returned to an unauthenticated caller on three procedures changes.
