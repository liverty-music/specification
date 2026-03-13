## Why

Dev environment testing revealed three related bugs that break the core authentication and user home flows: logout fails with 400 due to a URI mismatch, `UserService/Get` returns 500 because it requires a `user_id` parameter instead of resolving the caller from JWT claims, and the `homes` table schema has a redundant bidirectional reference (`users.home_id` + `homes.user_id`) that should be simplified to a single `users.home_id` foreign key.

## What Changes

- Fix `post_logout_redirect_uri` to include a trailing `/` to match the Zitadel-registered URI.
- Change `UserService/Get` to resolve the authenticated user from JWT claims (same pattern as `UpdateHome`), removing the `user_id` request field. **BREAKING**: `GetRequest.user_id` field removed; clients no longer provide a user ID.
- Remove `homes.user_id` column and its UNIQUE constraint / FK. The `users.home_id` FK becomes the sole reference direction. **BREAKING**: DB schema change requiring migration.
- Update all repository queries and Go code to JOIN on `users.home_id = homes.id` instead of `homes.user_id = users.id`.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `user-home`: Reference direction changes from `homes.user_id → users.id` to `users.home_id → homes.id`. Queries, Create, and UpdateHome repository methods updated accordingly.
- `user-auth`: `UserService/Get` changes from explicit `user_id` parameter to JWT-based caller resolution. Logout redirect URI fixed.

## Impact

- **specification**: `GetRequest` proto message changes (field removed) — breaking change, requires BSR release.
- **backend**: Repository layer (`user_repo.go`), handler (`user_handler.go`), DB schema (`schema.sql`), and Atlas migration.
- **frontend**: `auth-service.ts` (logout URI), `dashboard-service.ts` (remove `user_id` from `get()` call — already sends `{}`).
- **cloud-provisioning**: No changes needed (Zitadel registered URIs already have trailing `/`).
