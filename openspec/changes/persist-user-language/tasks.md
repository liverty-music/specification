## 1. Specification (proto)

- [x] 1.1 Add `optional string preferred_language` to `entity.v1.User` with `protovalidate` constraints `min_len: 2` and `pattern: "^[a-z]{2}$"`; document semantics (ISO 639-1, absent = NULL = not yet set by client)
- [x] 1.2 Add `optional string preferred_language` to `rpc.user.v1.CreateRequest` with the same `protovalidate` constraints; document idempotent-return non-overwrite rule and the absent-equals-backfill path for old clients
- [x] 1.3 Add `rpc UpdatePreferredLanguage(UpdatePreferredLanguageRequest) returns (UpdatePreferredLanguageResponse)` to `UserService`; define request (`UserId user_id`, `string preferred_language` with `min_len: 2` + pattern) and response (`User user`); document error matrix (INVALID_ARGUMENT / PERMISSION_DENIED / NOT_FOUND / UNAUTHENTICATED)
- [x] 1.4 Run `buf lint` and `buf format -w` locally; verify `buf breaking --against '.git#branch=main'` passes (all wire changes are additive — no `buf skip breaking` label required)
- [x] 1.5 Open specification PR; after approval and CI pass, merge to main
- [ ] 1.6 Cut GitHub Release `vX.Y.Z` on specification; monitor `buf-release.yml` until BSR gen completes

## 2. Backend (Go) — preparation while specification PR is in flight

- [x] 2.1 Create branch in backend worktree
- [x] 2.2 Draft Atlas migration: `ALTER TABLE app.users ALTER COLUMN preferred_language DROP DEFAULT;` and `UPDATE app.users SET preferred_language = NULL WHERE preferred_language = 'en';`; update column comment to document NULL semantics
- [x] 2.3 In `internal/adapter/rpc/mapper/user.go`, extend `UserToProto` to populate `preferred_language` when non-empty (using the proto `optional` field); extend `NewUserFromCreateRequest` to accept and pass through `preferred_language`
- [x] 2.4 In `internal/adapter/rpc/user_handler.go`, update the `Create` handler to read `preferred_language` from the request, validate it as part of the existing protovalidate interceptor, and propagate it to the use case
- [x] 2.5 In `internal/adapter/rpc/user_handler.go`, add `UpdatePreferredLanguage` handler with `RequireUserIDMatch` and proper error mapping
- [x] 2.6 In `internal/usecase/user_uc.go`, add `UpdatePreferredLanguage(ctx, userID, lang)` use-case method
- [x] 2.7 In `internal/infrastructure/database/rdb/user_repo.go`, add `UpdatePreferredLanguage(ctx, userID, lang) (*entity.User, error)` repo method that updates only the column and returns the refreshed row
- [x] 2.8 Update entity-level docs on `User.PreferredLanguage` (and `NewUser.PreferredLanguage`) to reflect "non-empty string supplied at signup; empty string disallowed by Create"
- [x] 2.9 Generate mocks via `mockery` for any new repository/use-case interface
- [x] 2.10 Write unit tests: mapper round-trip with present/absent preferred_language; use-case happy-path + NOT_FOUND; handler permission scoping
- [x] 2.11 Write integration test: Create persists preferred_language; idempotent Create does NOT overwrite; UpdatePreferredLanguage round-trips
- [x] 2.12 Run `make check` and verify all linters / tests pass

## 3. Frontend (Aurelia 2) — preparation while specification PR is in flight

- [x] 3.1 Create branch in frontend worktree
- [x] 3.2 In `src/main.ts`, change i18next-browser-languagedetector config to `caches: ['localStorage']`
- [x] 3.3 In `src/entities/user.ts`, add `preferredLanguage?: string` field to the `User` interface (proto optional → TS optional)
- [x] 3.4 In `src/adapter/rpc/client/user-client.ts`, update `create()` signature to accept and pass `preferredLanguage`; add `updatePreferredLanguage(userId, lang)` method that calls the new RPC
- [x] 3.5 In `src/services/user-service.ts`, expose `current.preferredLanguage`; add `updatePreferredLanguage(lang)` method with write-through state update
- [x] 3.6 In `src/services/user-hydration-task.ts`, after `ensureLoaded` resolves: if `current.preferredLanguage` is present call `i18n.setLocale(...)`; if absent call `userService.updatePreferredLanguage(i18n.getLocale())` (log warning on failure); always `localStorage.removeItem('language')`
- [x] 3.7 In `src/routes/auth-callback/auth-callback-route.ts`, on successful Create / ensureUserProvisioned, ensure `localStorage.removeItem('language')` runs (may be a no-op if hydration already did it, but keep for the explicit-Create path)
- [x] 3.8 In `src/services/user-service.ts` and the RPC client, ensure Create passes `i18n.getLocale()` as `preferredLanguage`
- [x] 3.9 In `src/util/change-locale.ts`, split anonymous vs authenticated paths: keep current behavior when unauthenticated; for authenticated callers route through `userService.updatePreferredLanguage(lang)` and DO NOT touch localStorage; surface RPC failure to the caller for UI feedback
- [x] 3.10 In `src/routes/settings/settings-route.ts`, rewrite `selectLanguage`: call the authenticated `changeLocale` path; on failure publish a Snack; reread `currentLocale` from `userService.current.preferredLanguage` after successful change
- [x] 3.11 Update unit tests in `src/routes/settings/settings-route.spec.ts` (and create equivalents for welcome if needed) to cover RPC success, RPC failure, and re-selection no-op
- [x] 3.12 Verify Storybook stories still render with the new `preferredLanguage` field on the User entity; update fixtures if needed
- [x] 3.13 Run `make check` and verify lint / typecheck / tests pass

## 4. Cross-Repo Release Coordination

- [ ] 4.1 Confirm specification PR merged and Release published (Task 1.6 complete) before pushing backend/frontend branches
- [ ] 4.2 In backend: `go get buf.build/gen/go/liverty-music/schema/...@vX.Y.Z`, `go mod tidy`, swap any `TODO: swap to generated type` placeholders for the real generated types, run `make check`
- [ ] 4.3 In frontend: `npm install @buf/liverty-music_schema.connectrpc_es@latest` (or the equivalent), swap placeholders for generated types, run `make check`
- [ ] 4.4 Open backend PR; address review; ensure CI passes before requesting merge
- [ ] 4.5 Open frontend PR; address review; ensure CI passes before requesting merge

## 5. Post-Merge Verification

- [ ] 5.1 After backend merge: monitor ArgoCD deployment via `gh run list --repo liverty-music/backend --branch main --limit 3`; verify new pod serves UpdatePreferredLanguage RPC (smoke test `grpcurl` or curl)
- [ ] 5.2 In dev environment: sign up a fresh test user, verify `app.users.preferred_language` matches the client locale at signup
- [ ] 5.3 In dev environment: take a legacy user row, sign in, verify hydration backfills `preferred_language` (DB transition NULL → 'ja'/'en')
- [ ] 5.4 In dev environment: change language via Settings, hard reload, verify the language persists (the original bug is fixed)
- [ ] 5.5 In dev environment: verify `localStorage['language']` is removed after sign-in and not re-written by any code path while authenticated
- [ ] 5.6 Archive the OpenSpec change via `/opsx:archive` once all tasks are ticked and verification is complete
