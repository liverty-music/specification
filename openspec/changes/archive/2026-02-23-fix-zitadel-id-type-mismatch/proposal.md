## Why

Zitadel uses snowflake-style numeric IDs (e.g., `360952429480515994`) for the `sub` claim, not UUIDs. The `users.external_id` column is typed `UUID`, causing user creation to fail. Additionally, the artist Follow/Unfollow/ListFollowed RPCs pass the Zitadel `sub` claim directly to queries against `followed_artists.user_id`, which references the internal `users.id` UUID — a second type mismatch that produces `SQLSTATE 22P02`. This blocks onboarding for all users on dev (backend#96).

## What Changes

- Change `users.external_id` column type from `UUID` to `TEXT` via a new Atlas migration
- Update the `User` protobuf entity to remove UUID format validation on `external_id`
- Inject `UserRepository` into `ArtistUseCase` so it can resolve `external_id → users.id`
- Update `Follow`, `Unfollow`, and `ListFollowed` use case methods to resolve the Zitadel sub claim to the internal user UUID before querying `followed_artists`

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `user-account-sync`: Change `external_id` type from UUID to TEXT to accept Zitadel snowflake IDs
- `artist-following`: Artist follow/unfollow/list operations must resolve external identity to internal user ID before database queries

## Impact

- **Database**: Migration to alter `users.external_id` from UUID to TEXT (data-compatible — existing UUIDs are valid TEXT)
- **Protobuf**: `User.external_id` field validation changes from `string.uuid` to plain string
- **Backend**: `ArtistUseCase` gains a `UserRepository` dependency; three methods updated
- **Frontend**: No changes required
