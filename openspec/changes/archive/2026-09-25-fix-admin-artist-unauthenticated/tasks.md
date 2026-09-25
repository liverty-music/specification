# Tasks

## 1. Infrastructure fix (admin server authentication wiring)

- [x] 1.1 In `internal/di/provider.go`, construct a dedicated `authn.AuthFunc` for the admin server via `auth.NewAuthFunc(jwtValidator, nil)` (no public procedures, ever) and pass it to the admin `server.NewConnectServer(...)` call instead of the consumer server's `authFunc`; keep the consumer server's `authFunc`/`publicProcedures` unchanged
- [x] 1.2 In `internal/infrastructure/auth/context.go`, change `RequireRole` to return `connect.CodeUnauthenticated` (not `CodePermissionDenied`) when `GetClaims` finds no claims, keeping `CodePermissionDenied` for the case where claims are present but the role is missing; update the function's doc comment to match
- [x] 1.3 Update `internal/infrastructure/auth/authz_test.go`'s `TestRequireRoleInterceptor_WrapUnary` "deny unauthenticated caller (no claims)" case to expect `connect.CodeUnauthenticated`; add a direct `TestRequireRole` (or extend `context_test.go`) covering both branches (no claims -> Unauthenticated, claims without role -> PermissionDenied, claims with role -> nil)
- [x] 1.4 Add a table test exercising the admin server's registered procedures (at minimum `ArtistService/ListTop`, `ArtistService/ListSimilar`, `ArtistService/Search`, plus one ordinary admin-only method such as `ConcertService/ListPending`) for: unauthenticated -> Unauthenticated, signed-in non-admin -> PermissionDenied, admin -> request reaches the usecase/handler; verify with `go test ./internal/di/... -run TestAdminServer` (or the package the test lands in, per project convention — colocate with existing `internal/di` or `internal/infrastructure/server` tests, whichever already exercises the wired admin server)

## 2. Adapter (components/adapter/admin/api/rpc/artist)

- [x] 2.1 Verify/extend the admin `ArtistHandler`-level or admin-server-level tests to cover all four spec scenarios: "Admin searches for an artist" (Search succeeds for a signed-in admin), "Signed-in caller without the admin role" (Search fails PermissionDenied), "Guest browses" (ListTop fails Unauthenticated for no sign-in), "Guest creates" (Create fails Unauthenticated for no sign-in); annotate each test/subtest with `// @spec components/adapter/admin/api/rpc/artist "<scenario name>"` exactly matching the scenario names above; run with `go test ./internal/di/... ./internal/infrastructure/... -run <relevant test names>`

## 3. Verification

- [x] 3.1 Run `make lint` and `go test ./...` (excluding integration) and confirm both pass; confirm no other admin procedure's behavior changed (spot-check `ConcertService`, `OrganizerService`, `OrderAdminService` unauthenticated/non-admin cases still pass their existing specs)
