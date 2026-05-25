## 1. Specification (proto)

- [x] 1.1 Add `optional string preferred_language` to `entity.v1.User` with `protovalidate` constraints `min_len: 2` and `pattern: "^[a-z]{2}$"`; document semantics (ISO 639-1, absent = NULL = not yet set by client)
- [x] 1.2 Add `optional string preferred_language` to `rpc.user.v1.CreateRequest` with the same `protovalidate` constraints; document idempotent-return non-overwrite rule and the absent-equals-backfill path for old clients
- [x] 1.3 Add `rpc UpdatePreferredLanguage(UpdatePreferredLanguageRequest) returns (UpdatePreferredLanguageResponse)` to `UserService`; define request (`UserId user_id`, `string preferred_language` with `min_len: 2` + pattern) and response (`User user`); document error matrix (INVALID_ARGUMENT / PERMISSION_DENIED / NOT_FOUND / UNAUTHENTICATED)
- [x] 1.4 Run `buf lint` and `buf format -w` locally; verify `buf breaking --against '.git#branch=main'` passes (all wire changes are additive — no `buf skip breaking` label required)
- [x] 1.5 Open specification PR; after approval and CI pass, merge to main
- [x] 1.6 Cut GitHub Release `vX.Y.Z` on specification; monitor `buf-release.yml` until BSR gen completes

## 2. Backend (Go) — initial PR #304

- [x] 2.1 Create branch in backend worktree
- [x] 2.2 Draft Atlas migration: `ALTER TABLE app.users ALTER COLUMN preferred_language DROP DEFAULT;` and `UPDATE app.users SET preferred_language = NULL WHERE preferred_language IS NOT NULL`; update column comment to document NULL semantics
- [x] 2.3 In `internal/adapter/rpc/mapper/user.go`, extend `UserToProto` to populate `preferred_language` when non-empty (using the proto `optional` field); extend `NewUserFromCreateRequest` to accept and pass through `preferred_language`
- [x] 2.4 In `internal/adapter/rpc/user_handler.go`, update the `Create` handler to read `preferred_language` from the request, validate it as part of the existing protovalidate interceptor, and propagate it to the use case
- [x] 2.5 In `internal/adapter/rpc/user_handler.go`, add `UpdatePreferredLanguage` handler with `RequireUserIDMatch` and proper error mapping
- [x] 2.6 In `internal/usecase/user_uc.go`, add `UpdatePreferredLanguage(ctx, userID, lang)` use-case method
- [x] 2.7 In `internal/infrastructure/database/rdb/user_repo.go`, add `UpdatePreferredLanguage(ctx, userID, lang) (*entity.User, error)` repo method that updates only the column and returns the refreshed row
- [x] 2.8 Update entity-level docs on `User.PreferredLanguage` (and `NewUser.PreferredLanguage`) to reflect "non-empty string supplied at signup; empty string disallowed by Create"
- [x] 2.9 Generate mocks via `mockery` for any new repository/use-case interface
- [x] 2.10 Write unit tests: mapper round-trip with present/absent preferred_language; use-case happy-path + NOT_FOUND; handler permission scoping
- [x] 2.11 Write integration test: Create persists preferred_language; idempotent Create does NOT overwrite; UpdatePreferredLanguage round-trips
- [x] 2.12 Run `make check` and verify all linters / tests pass — PR #304 merged as commit `392d823`

## 3. Frontend (Aurelia 2) — initial PR #366

- [x] 3.1 Create branch in frontend worktree
- [x] 3.2 In `src/main.ts`, change i18next-browser-languagedetector config to `caches: ['localStorage']`
- [x] 3.3 In `src/entities/user.ts`, add `preferredLanguage?: string` field to the `User` interface (proto optional → TS optional)
- [x] 3.4 In `src/adapter/rpc/client/user-client.ts`, update `create()` signature to accept and pass `preferredLanguage`; add `updatePreferredLanguage(userId, lang)` method that calls the new RPC
- [x] 3.5 In `src/services/user-service.ts`, expose `current.preferredLanguage`; add `updatePreferredLanguage(lang)` method with write-through state update
- [x] 3.6 In `src/services/user-hydration-task.ts`, after `ensureLoaded` resolves: if `current.preferredLanguage` is present call `i18n.setLocale(...)`; if absent call `userService.updatePreferredLanguage(i18n.getLocale())` (log warning on failure); always `localStorage.removeItem('language')`
- [x] 3.7 In `src/routes/auth-callback/auth-callback-route.ts`, on successful Create / ensureUserProvisioned, ensure `localStorage.removeItem('language')` runs
- [x] 3.8 In `src/services/user-service.ts` and the RPC client, ensure Create passes `i18n.getLocale()` as `preferredLanguage`
- [x] 3.9 In `src/util/change-locale.ts`, split anonymous vs authenticated paths: keep current behavior when unauthenticated; for authenticated callers route through `userService.updatePreferredLanguage(lang)` and DO NOT touch localStorage; surface RPC failure to the caller for UI feedback
- [x] 3.10 In `src/routes/settings/settings-route.ts`, rewrite `selectLanguage`: call the authenticated `changeLocale` path; on failure publish a Snack; reread `currentLocale` from `userService.current.preferredLanguage` after successful change
- [x] 3.11 Update unit tests in `src/routes/settings/settings-route.spec.ts` (and create equivalents for welcome if needed) to cover RPC success, RPC failure, and re-selection no-op
- [x] 3.12 Verify Storybook stories still render with the new `preferredLanguage` field on the User entity; update fixtures if needed
- [x] 3.13 Run `make check` and verify lint / typecheck / tests pass — PR #366 merged as commit `1ccec98`

## 4. Cross-Repo Release Coordination (initial)

- [x] 4.1 Confirm specification PR merged and Release published (Task 1.6 complete) before pushing backend/frontend branches
- [x] 4.2 In backend: `go get buf.build/gen/go/liverty-music/schema/...@vX.Y.Z`, `go mod tidy`, swap any `TODO: swap to generated type` placeholders for the real generated types, run `make check`
- [x] 4.3 In frontend: `npm install @buf/liverty-music_schema.connectrpc_es@latest` (or the equivalent), swap placeholders for generated types, run `make check`
- [x] 4.4 Open backend PR; address review; ensure CI passes before requesting merge
- [x] 4.5 Open frontend PR; address review; ensure CI passes before requesting merge

## 5. Post-Merge Verification — incident recovery (added 2026-05-23)

The dev environment has been unreachable from operator workstations since 2026-05-19 (TLS handshake fails on `dev.liverty-music.app` and the autopilot GKE control-plane endpoint times out from external networks). Verification therefore runs against prod, gated by the deploy-order rule from design D10.

- [x] 5.1 Connect to prod Cloud SQL via `kubectl port-forward` against `cloud-sql-proxy` in the autopilot cluster; verify `app.users` rows for the affected accounts have `external_id` matching the current JWT `sub` AND `preferred_language` is NULL (confirms the migration ran on prod ahead of the backend fix)
- [x] 5.2 Reproduce the symptom in a browser session for one affected account; confirm the failing path is `UserService.Get` returning `not_found` (cache-hit path) and `UserService.Create` returning `already_exists` (cache-miss path)
- [x] 5.3 Diagnose: confirm via `gcloud logging read` that the backend logs `"duplicate user"` immediately followed by the access log entry with `status=already_exists`, and that the row is fetchable directly via psql with the EXACT `userColumns` SELECT — pinpointing scan-NULL-to-`string` as the failure
- [x] 5.4 Pod-restart hypothesis test: `kubectl rollout restart deployment/server-app` against prod; confirm the symptom persists (rules out pgx connection-pool snapshot staleness)
- [x] 5.5 Code audit: confirm `origin/main:internal/infrastructure/database/rdb/user_repo.go` already uses `sql.NullString` for `preferred_language` and the `nullStringFromEmpty` helper exists, but does NOT extend the pattern to `country` and `time_zone`; confirm `userUseCase.Create`'s retry collapses every `GetByExternalID` error into the original AlreadyExists (D9 gap)

## 6. Backend follow-up PR — D8 extension + D9 + recovery (added 2026-05-23)

This work is NOT in PR #304. Shipped in backend PR #307 (commits `9d0ecf9` + `5cd78ca`) → tag `v1.1.1`.

- [x] 6.1 In `internal/infrastructure/database/rdb/user_repo.go`, extend the `sql.NullString` scan pattern to `country` and `time_zone` (`scanUser` already does it for `preferred_language` per PR #304; the same intermediate-local approach applies). Use the existing `homeID/countryCode/level1/level2` pattern as the reference. `safe_address` — the fourth nullable column listed in design D8 — is intentionally NOT migrated to `sql.NullString`; it was already NULL-safe from its introduction commit via the SQL-side `COALESCE(u.safe_address, '')` projection in `userColumns`. Per the spec's "Repository NULL-Safe Reads" requirement, COALESCE is an accepted equivalent pattern, so changing it would be churn for no behavior change.
- [x] 6.2 In `internal/usecase/user_uc.go`, change `Create`'s retry-on-AlreadyExists branch to inspect the `GetByExternalID` error's apperr code (`codes.NotFound` vs anything else) and return the actual error when it is not `NotFound`. Log a WARN with both errors so the operator has the full chain. Reference: design D9.
- [x] 6.3 In `internal/infrastructure/database/rdb/user_repo_test.go`, add a NULL-row case for every existing scan-exercising test (`Get`, `GetByExternalID`, `GetByEmail`, `List`, `Update`, `UpdateHome`). `TestUserRepository_ScanNULLColumns` covers all of these in a single regression gate.
- [x] 6.4 In `internal/usecase/user_uc_test.go`, add a test for the D9 branching: stub the repo to return `Internal` from `GetByExternalID`; assert the use case returns the `Internal` error (not `AlreadyExists`); stub `NotFound` and assert the original `AlreadyExists` propagates. Shipped as a table-driven subtest covering Internal + Unavailable retry classes.
- [x] 6.5 Run `make check`; open follow-up backend PR; address review; merge. (PR #307 merged as commit `aae5228`.)
- [x] 6.6 Cut a new backend `v1.1.1` Release; verify `Deploy Backend` workflow promotes the image to prod AR.

## 7. Prod recovery rollout (added 2026-05-23)

- [x] 7.1 Pre-flight: `kubectl describe deployment/server-app -n backend --context=<prod>` and confirm the deployed image tag corresponds to the commit from Task 6.5 — completed via cloud-provisioning PR #302 (backend overlay → v1.1.1) and ArgoCD sync (pod `server-app-69ff69cbd4-p8x4s` confirmed on `:v1.1.1`).
- [x] 7.2 Reproduce in a browser session for one of the affected prod accounts; confirm `UserService.Get` now returns the user with `preferredLanguage` absent (NULL → omitted via proto `optional`). Note: prod row was diagnostic-set to `'ja'` during incident response so the proto carries the value; the scan-NULL fix is verified via the new test suite rather than re-induced in prod.
- [x] 7.3 Confirm the frontend hydration task fires `UpdatePreferredLanguage(i18n.getLocale())` on observing the absence; confirm the DB row's `preferred_language` is now populated.
- [x] 7.4 Hard-reload; confirm i18n shows the language from the DB (the original symptom is fixed). Required frontend release `v1.1.1` → `v1.1.2` because the v1.1.0 bundle (still served by prod overlay pinned to v1.1.0 at the time) lacked PR #366's mapper consumption. cloud-provisioning PR #304 (frontend overlay → v1.1.1) + frontend release v1.1.2 completed the chain.
- [x] 7.5 Change language via Settings; confirm the RPC succeeds, the DB row updates, and a subsequent hard reload preserves the choice. Verified.
- [x] 7.6 Spot-check `localStorage['language']` in the same browser session; confirm it is absent after hydration AND remains absent after Settings change.

## 8. Post-recovery refactor — Settings view state SSoT (added 2026-05-25)

Prod verification of v1.1.2 surfaced a residual reactivity bug: after Settings.selectLanguage succeeded, reopening the Language selector still highlighted the OLD language with a check-mark. Root cause: `if.bind="isCurrentLanguage(lang)"` is a method-call expression that Aurelia's expression observer cannot track property accesses through. The same anti-pattern (local-mirror-of-entity-state) existed for `currentHome` plus a guest-storage fallback that bypassed the user entity.

Shipped in frontend PR #369 (`refactor(user): derive Settings view from observable UserService.current`) → tag `v1.1.2` (sic: same tag re-cut after the PR merged, since v1.1.1 hadn't been released yet at the time of original tagging).

- [x] 8.1 `UserService._current` (private) → `@observable public current` so Aurelia's expression observer subscribes directly to the change notification channel.
- [x] 8.2 `SettingsRoute`: drop local mirror fields `currentLocale` and `currentHome`; replace with computed getters that derive from `userService.current` directly. Drop the manual `this.currentLocale = ...` write-back in `selectLanguage()`, the copy step in `loading()`, and the `UserHomeSelector.getStoredHome()` guest-flow fallback (Settings is authenticated-only).
- [x] 8.3 `onHomeSelected`: collapse to a notification-only handler — UserHomeSelector already owns the `userService.updateHome` call, and the derived getter surfaces the result automatically.
- [x] 8.4 Template: inline `currentLocale === lang` in the Language selector's `if.bind` and `data-selected.bind` so the expression observer subscribes to `currentLocale` directly (eliminates the method-call indirection). Remove the `isCurrentLanguage()` helper.
- [x] 8.5 Tests: assert getters derive from `userService.current` WITHOUT a `loading()` re-run; `onHomeSelected` no longer mutates state.
- [x] 8.6 Frontend release `v1.1.2` cut; cloud-provisioning PR #308 bumps frontend prod overlay; ArgoCD syncs new bundle (`index-DKh5HSGA.js`); browser re-verified — selector check-mark moves correctly across multiple language toggles within the same session.

## 9. Dev environment unblock (out-of-band, tracked separately)

The dev environment has been unreachable from operator workstations since 2026-05-19 (TLS handshake fails on `dev.liverty-music.app`; the autopilot GKE control-plane endpoint times out from external networks). This blocked every verification step from running in dev and forced the prod-only recovery path documented in §7. Out of scope for this change.

- [ ] 9.1 Resolve the dev environment TLS / control-plane unreachability (filed under separate incident). Once dev is reachable, re-run the §7 verification in dev to lock in the rollback path for future migrations.

## 10. Follow-up refactors deferred to separate PRs (added 2026-05-25)

Identified during the §8 audit but intentionally not bundled with this change to keep scope focused:

- [ ] 10.1 **AuthService claim-derived state**: move the `auth.user?.profile.email_verified` cast leakage out of `SettingsRoute.emailVerified` into an `AuthService.isEmailVerified` getter. Also consider `@observable` on `auth.user` so the bindings push-update instead of dirty-check.
- [ ] 10.2 **Consolidate post-auth `i18n.setLocale` logic**: auth-callback-route and user-hydration-task share the "apply preferred language to i18n if supported" decision; extract to a `UserService.applyPreferredLanguageToI18n()` (or similar helper) so both call sites converge.
- [ ] 10.3 **UserId localStorage cache adapter**: extract the `userIdStorageKey` read/write/remove trio from UserService into a dedicated `IUserIdCache` adapter to separate bootstrap-optimization concerns from CRUD.
- [ ] 10.4 **UserHomeSelector catch-swallow**: `confirmSelection` catches `updateHome` errors and unconditionally calls `onHomeSelected?.(code)`, so failed updates surface as successful UI feedback. Surface the failure (Snack) and skip the success callback on failure.

## 11. Archive

- [x] 11.1 Once §6 / §7 / §8 are complete AND the affected prod accounts are self-healed (verified via §7.4 + §8.6), archive the OpenSpec change via `/opsx:archive`. §9 and §10 stay open as deferred work tracked under separate scopes.
