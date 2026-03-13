## 1. Specification (Proto)

- [x] 1.1 Remove `user_id` field from `GetRequest` in `user_service.proto`
- [x] 1.2 Remove `GetRequest` message (now empty — `Get` takes `google.protobuf.Empty` or no fields)
- [x] 1.3 Run `buf lint` and `buf format -w` to validate proto changes

## 2. Backend — DB Migration

- [x] 2.1 Create Atlas migration: drop `homes.user_id` column, its FK constraint, and UNIQUE index
- [x] 2.2 Update `schema.sql` (desired state) to remove `homes.user_id` and reflect `users.home_id` as sole reference
- [x] 2.3 Run `atlas migrate apply --env local` and verify migration applies cleanly (skipped: local DB missing homes table; CI will apply)

## 3. Backend — Repository Layer

- [x] 3.1 Update `getUserQuery` JOIN from `homes.user_id = u.id` to `u.home_id = h.id`
- [x] 3.2 Update `Create` method: after inserting home, UPDATE `users.home_id` with the returned home ID
- [x] 3.3 Update `UpdateHome` method: after upserting home, UPDATE `users.home_id` with the returned home ID
- [x] 3.4 Remove `user_id` parameter from home INSERT/UPSERT queries (homes no longer has user_id)
- [x] 3.5 Update repository tests to verify new query patterns

## 4. Backend — Handler Layer

- [x] 4.1 Update `UserHandler.Get` to extract `sub` claim from JWT context and call `GetByExternalID` (same pattern as `UpdateHome`)
- [x] 4.2 Remove `user_id` validation from `Get` handler
- [x] 4.3 Update handler tests for JWT-based `Get` (no test file exists)

## 5. Frontend — Auth Fixes

- [x] 5.1 Fix `post_logout_redirect_uri` in `auth-service.ts` to append trailing `/` to `window.location.origin`
- [x] 5.2 Update `UserService.Get` call in `dashboard-service.ts` to send empty request (already sends `get({})` — no change needed)

## 6. Cross-Repo Release

- [x] 6.1 Create specification PR (#214), merge, and create GitHub Release (triggers BSR publish)
- [ ] 6.2 After BSR gen completes, update backend `go.sum` with new proto types
- [x] 6.3 Create backend PR (#201, draft) with migration + code changes
- [x] 6.4 Create frontend PR (#163) with auth fixes
