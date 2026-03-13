## Context

Three bugs were discovered during dev environment testing:

1. **Logout 400**: `oidc-client-ts` sends `window.location.origin` (no trailing `/`) as `post_logout_redirect_uri`, but Zitadel has `https://dev.liverty-music.app/` (with trailing `/`) registered. Exact string match fails.
2. **UserService/Get 500**: The `GetRequest` proto requires `user_id`, but the frontend calls `get({})` to fetch "my profile". The dashboard's `fetchUserHome()` fails, causing the home selector to reappear every page load even though `homes` records exist.
3. **Bidirectional home reference**: `users.home_id → homes.id` AND `homes.user_id → users.id` both exist. Only `homes.user_id` is used in queries; `users.home_id` is never populated. This should be simplified to `users.home_id` as the sole FK.

## Goals / Non-Goals

**Goals:**

- Fix logout flow so users can sign out successfully.
- Make `UserService/Get` resolve the caller from JWT claims, consistent with `UpdateHome`.
- Simplify the homes schema to a single reference direction: `users.home_id → homes.id`.
- Ensure existing dev data is preserved through the migration.

**Non-Goals:**

- Changing the Zitadel-registered URIs (they follow OIDC convention with trailing `/`).
- Adding new features to user home or auth flows.
- Fixing the bottom nav bar scroll issue (tracked separately).

## Decisions

### 1. Fix logout URI in frontend, not in Zitadel config

Append `/` to `window.location.origin` in `auth-service.ts`. OIDC convention uses trailing slashes for redirect URIs, and the Zitadel registration already follows this. Changing the Zitadel config would require `pulumi up` and could affect other environments.

### 2. UserService/Get resolves caller from JWT claims

Remove `user_id` from `GetRequest` proto. The backend handler extracts the `sub` claim from JWT context and calls `GetByExternalID` — the same pattern `UpdateHome` already uses. This is a breaking proto change but aligns all user-facing RPCs to a consistent "act on the authenticated caller" pattern.

Alternative considered: Keep `user_id` optional and fall back to JWT when absent. Rejected because `Get` with an explicit `user_id` for other users is not a current requirement and adds complexity.

### 3. Reference direction: `users.home_id → homes.id`

Drop `homes.user_id` column and its UNIQUE constraint. Keep `users.home_id` as the sole FK to `homes.id`. This means:

- `homes` becomes a pure value table (id, country_code, level_1, level_2, timestamps).
- The 1:1 relationship is enforced by `users.home_id` being a FK with `ON DELETE SET NULL`.
- All queries change from `LEFT JOIN homes h ON h.user_id = u.id` to `LEFT JOIN homes h ON u.home_id = h.id`.
- `Create` and `UpdateHome` repo methods must UPDATE `users.home_id` after inserting/upserting into `homes`.

Alternative considered: Drop `users.home_id` and keep `homes.user_id`. Rejected because the user is the owning entity; `users → homes` is the more natural direction.

### 4. Migration strategy

1. **Pre-migration data fix** (manual, already done): `UPDATE users SET home_id = h.id FROM homes h WHERE h.user_id = users.id`.
2. **Atlas migration**: Drop `homes.user_id` column, its FK constraint, and UNIQUE index. Add NOT NULL constraint considerations for `homes` rows that no longer have a user reference.
3. Since `homes.id` uses `gen_random_uuid()` (not UUIDv7), existing IDs are preserved. The migration is additive (drop column) — rollback would require re-adding the column and backfilling.

## Risks / Trade-offs

- **Breaking proto change** (`GetRequest.user_id` removed) → Requires specification PR, BSR release, then backend + frontend updates in dependency order. Mitigated by following the standard cross-repo release workflow.
- **Orphaned homes rows** → After dropping `homes.user_id`, homes rows no longer reference their owner directly. The relationship is only discoverable via `users.home_id`. If a user row is deleted, `ON DELETE SET NULL` on `users.home_id` leaves the homes row orphaned. Acceptable for now; a cleanup job can be added later if needed, or we can add `ON DELETE CASCADE` from users to homes via a trigger.
- **Dev DB data** → Pre-migration UPDATE must be run before deploying the migration. Already communicated to the team.
