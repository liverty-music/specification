## Why

The user's preferred display language was stored only in browser `localStorage`. That is unreliable (Safari ITP 7-day cap, private browsing, cross-device divergence) and was the suspected cause of authenticated users seeing the UI revert to EN after a hard reload. The DB had a `users.preferred_language` column with `DEFAULT 'en'` but never exposed it over the wire, so it could not serve as a source of truth.

This change makes the DB authoritative for authenticated users while keeping browser auto-detection working pre-signup and removing `localStorage['language']` once the user signs up.

**Post-merge revision (2026-05-23).** Initial implementation merged across specification (`vX.Y.Z`), backend (PR #304, commit `392d823`), and frontend (PR #366, commit `1ccec98`). Manual prod verification then exposed a **previously latent backend bug** that the new migration triggered:

- `UserRepository.scanUser` scanned the nullable `preferred_language` column into a Go `string` field. Before this change every existing row had `'en'` (the dropped DEFAULT), so the bug never fired. The new migration `UPDATE users SET preferred_language = NULL WHERE preferred_language IS NOT NULL` flipped every existing row to NULL, and every subsequent `UserService.Get`/`Create` call on those rows started returning `not_found` / `already_exists` because `pgx` cannot scan NULL into a non-nullable `*string`.
- PR #304 incidentally fixed the scan for `preferred_language` (switched to `sql.NullString` + a `nullStringFromEmpty` write boundary helper). But prod still serves `v1.1.0`, which does NOT contain that fix. The migration ran on prod ahead of the deploy; result: prod hydration is broken for every existing user until the next backend release lands.
- Two other nullable columns scanned the same unsafe way — `users.country`, `users.time_zone` — and remain raw `string` even on origin/main. They are not failing today only because no row currently has NULL in those columns. This is a latent recurrence waiting for the next migration that introduces NULLs.
- The Create idempotent-retry path (`AlreadyExists` → `GetByExternalID` → re-return existing user) interpreted *any* `GetByExternalID` error as "row not found, propagate the original AlreadyExists". A scan error therefore surfaces to the client as `AlreadyExists` instead of `Internal`, masking the actual fault and making this incident much harder to diagnose.

This rewrite folds those discoveries into the scope: the data-state change is unchanged, but the repository layer SHALL be NULL-safe across all nullable user columns, the migration SHALL not deploy ahead of a backend that can read its post-state, and the Create retry SHALL distinguish "not found" from "scan/transport failure".

## What Changes

### Schema and RPC surface (unchanged from initial)

- `entity.v1.User` adds an optional `preferred_language` field (ISO 639-1). Additive, wire-compatible.
- `rpc.user.v1.CreateRequest` adds an optional `preferred_language` field. Old clients that omit it create rows with NULL `preferred_language` and rely on the hydration backfill path.
- Add `UserService.UpdatePreferredLanguage(user_id, preferred_language)` (mirrors `UpdateHome`).
- Drop `DEFAULT 'en'` on `users.preferred_language`; UPDATE legacy rows to NULL so the client owns the value going forward.
- Backend: extend `UserToProto` and `NewUserFromCreateRequest` to carry the field; add `UpdatePreferredLanguage` handler / use case / repo method.
- Frontend: change i18next-browser-languagedetector to `caches: ['localStorage']`; pass `i18n.getLocale()` as `preferred_language` on Create; on hydration apply DB value or backfill via `UpdatePreferredLanguage`; remove `localStorage['language']` once authenticated; route Settings language change through the new RPC.

### NULL-safety and recovery (added post-merge)

- `UserRepository.scanUser` SHALL scan every nullable `users` column (`preferred_language`, `country`, `time_zone`, `safe_address`) through a NULL-aware intermediate (`sql.NullString` or `COALESCE` at the SQL boundary). Bare `string` scans on nullable columns SHALL be removed from this repository.
- A `nullStringFromEmpty` (or equivalent) write boundary helper SHALL be used on INSERT/UPDATE so callers can keep the Go-side empty-string-as-absent convention while the column distinguishes NULL from `''`.
- `userUseCase.Create`'s idempotent retry SHALL only treat `GetByExternalID` returning `codes.NotFound` as "different row collided" (= return the original AlreadyExists). Any other error class (Internal, Unavailable, scan failure) SHALL be wrapped and returned so the operator sees the real failure, not a masquerading AlreadyExists.
- The Atlas migration that introduces NULLs SHALL NOT be deployed to an environment whose currently-running backend image cannot scan NULLs in the affected columns. The operator runbook captures the version gate.
- Prod recovery: once the backend image carrying the scan fix is in prod, the existing two prod rows self-heal via the standard hydration-backfill path (Get returns row with empty `preferredLanguage` → frontend calls `UpdatePreferredLanguage(i18n.getLocale())`). No data backfill SQL is required.

## Capabilities

### New Capabilities

- `user-language-preference`: Backend ownership of the authenticated user's preferred display language — proto field, Create/Update RPCs, DB column semantics, repo-layer NULL safety, and the contract that DB is the source of truth post-signup.

### Modified Capabilities

- `frontend-i18n`: Locale detection caches the detected value to `localStorage`. Authenticated runtime switching routes through the backend RPC.
- `settings`: Language row reads from `UserService.current.preferred_language` and writes via `UpdatePreferredLanguage`. No `localStorage` reads or writes.
- `user-profile-hydration`: After loading the user, apply `preferred_language` to i18n or backfill via `UpdatePreferredLanguage` when absent. Cleanup `localStorage['language']`.
- `user-account-sync`: `Create` accepts `preferred_language`. Idempotent-return does NOT overwrite an existing user's value (same rule as `home`).

## Impact

- **Proto / BSR**: `User.preferred_language` and `CreateRequest.preferred_language` added (both `optional`); new `UpdatePreferredLanguage` RPC. Additive; `buf breaking` passes. Released as a minor schema bump.
- **Backend (Go)**: `internal/adapter/rpc/mapper/user.go`, `internal/adapter/rpc/user_handler.go`, `internal/usecase/user_uc.go`, `internal/infrastructure/database/rdb/user_repo.go`, Atlas migration `20260521083536_drop_users_preferred_language_default.sql`. **Additional repo work**: `scanUser` made NULL-safe for `country` and `time_zone`; `userUseCase.Create` retry path tightened to error-class-aware branching; tests for NULL-column rows added across `Get`, `GetByExternalID`, `GetByEmail`, `List`, and `Update`.
- **Frontend (Aurelia 2)**: as enumerated in the prior revision (`main.ts`, `entities/user.ts`, `adapter/rpc/client/user-client.ts`, `services/user-service.ts`, `services/user-hydration-task.ts`, `routes/auth-callback/auth-callback-route.ts`, `routes/settings/settings-route.ts`, `util/change-locale.ts`). No further frontend changes needed by this rewrite.
- **Database**: `app.users.preferred_language` — DEFAULT dropped, existing rows updated to NULL. No additional migration required for the post-merge fix because the row state already matches the spec; prod recovery happens via hydration backfill once the new backend image deploys.
- **Cross-repo release order**: specification PR + Release → BSR gen → backend & frontend PRs. **Added gate**: backend release containing the `scanUser` fix MUST be promoted to a given environment BEFORE that environment's Atlas migration runs the legacy-row NULL UPDATE. Operators verify this via the runbook in `tasks.md` §5.
