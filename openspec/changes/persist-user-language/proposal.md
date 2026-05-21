## Why

The user's preferred display language is currently stored only in browser `localStorage`, which is unreliable (Safari 7-day cap, private browsing, cross-device divergence) and is the suspected cause of authenticated users seeing the UI revert to EN after a hard reload. The DB already has a `users.preferred_language` column but it is never exposed over the wire, so it cannot serve as a source of truth. We need to make the DB authoritative for authenticated users while keeping the existing browser auto-detection working pre-signup, and clean up localStorage as soon as the user signs up.

## What Changes

- `entity.v1.User` adds an optional `preferred_language` field (ISO 639-1). Additive only — wire-compatible.
- `rpc.user.v1.CreateRequest` adds an optional `preferred_language` field. Wire-compatible — old clients that omit the field create users with NULL preferred_language and trigger the same hydration-backfill path as legacy rows. Updated clients always send the value.
- Add new RPC `UserService.UpdatePreferredLanguage(user_id, preferred_language)` (mirrors the existing `UpdateHome` custom-method pattern).
- Backend: remove the `DEFAULT 'en'` from `users.preferred_language`, set existing rows to `NULL` so the client can backfill on next hydration.
- Backend: extend `UserToProto` and `NewUserFromCreateRequest` to carry `preferred_language`; add a `UpdatePreferredLanguage` handler/use-case/repo method.
- Frontend: change i18n detector config to cache detected locale to `localStorage` (so first-visit browser detection persists).
- Frontend: on signup (Create), send `i18n.getLocale()` as `preferred_language`; on success, remove `localStorage['language']`.
- Frontend: on profile hydration (Get), if `user.preferred_language` is set, switch i18n to it; if absent (NULL), call `UpdatePreferredLanguage` with the current effective locale to backfill.
- Frontend: Settings → Language change calls `UpdatePreferredLanguage` and `i18n.setLocale`; it MUST NOT touch `localStorage`.
- Frontend: while authenticated, no code path reads or writes `localStorage['language']`.

## Capabilities

### New Capabilities

- `user-language-preference`: Backend ownership of the authenticated user's preferred display language — proto entity field, Create/Update RPCs, DB column semantics, and the contract that DB is the source of truth post-signup.

### Modified Capabilities

- `frontend-i18n`: Locale detection now persists the detected value to `localStorage` (cache enabled). Runtime switching for authenticated users routes through the backend RPC; the shared `changeLocale` utility no longer touches `localStorage` for authenticated callers.
- `settings`: The Language row reads from `UserService.current.preferred_language` and writes via `UpdatePreferredLanguage`. It MUST NOT read or write `localStorage['language']`.
- `user-profile-hydration`: After loading the User entity, the frontend applies `user.preferred_language` to i18n. When the field is empty (NULL legacy rows), the frontend backfills it by calling `UpdatePreferredLanguage` with the currently effective locale. The hydration step also removes any lingering `localStorage['language']`.
- `user-account-sync`: The `Create` RPC accepts `preferred_language`, captured at sign-up from the client's effective locale. After successful Create, the frontend removes `localStorage['language']`. The idempotent-return path does NOT overwrite an existing user's `preferred_language` (mirrors the existing rule for `home`).

## Impact

- **Proto / BSR**: `User.preferred_language` field added; `CreateRequest.preferred_language` added (both `optional`); new `UpdatePreferredLanguage` RPC. Will be released as a minor version bump in the BSR schema. All wire changes are additive — `buf breaking` passes and old clients keep working through the optional-field semantics (their Create calls succeed with `preferred_language` NULL on the resulting row).
- **Backend (Go)**: `internal/adapter/rpc/mapper/user.go` (mapper extension), `internal/adapter/rpc/user_handler.go` (new RPC), `internal/usecase/user_uc.go` (new use-case method), `internal/infrastructure/database/rdb/user_repo.go` (language-only update). Atlas migration to drop `DEFAULT 'en'` and NULL out existing rows.
- **Frontend (Aurelia 2)**: `src/main.ts` (i18n detector `caches: ['localStorage']`), `src/entities/user.ts` (add field), `src/adapter/rpc/client/user-client.ts` (new method + Create signature), `src/services/user-service.ts`, `src/services/user-hydration-task.ts` (apply + backfill), `src/routes/auth-callback/auth-callback-route.ts` (cleanup localStorage), `src/routes/settings/settings-route.ts` (route through RPC), `src/util/change-locale.ts` (split: anon vs authed paths).
- **Database**: `app.users.preferred_language` — DEFAULT dropped, existing rows updated to NULL.
- **Cross-repo release order**: specification PR + Release → BSR gen → backend & frontend PRs (per the standard proto-change workflow).
