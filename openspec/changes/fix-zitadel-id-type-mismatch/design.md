## Context

The backend uses Zitadel as its identity provider. Zitadel issues JWT tokens where the `sub` claim is a snowflake-style numeric string (e.g., `360952429480515994`), not a UUID. The `users.external_id` column was created as `UUID` type, which rejects non-UUID values at INSERT time — blocking user creation entirely. Separately, the artist Follow/Unfollow/ListFollowed RPCs extract the Zitadel `sub` from the JWT and pass it directly to queries against `followed_artists.user_id`, which references the internal `users.id` (UUIDv7). This is a second mismatch: even if the user existed, the wrong ID type is used for artist queries.

## Goals / Non-Goals

**Goals:**
- Accept Zitadel snowflake IDs in `users.external_id` by changing the column type to TEXT
- Resolve external identity to internal user UUID in artist use case methods before database queries
- Unblock the onboarding flow on dev environment

**Non-Goals:**
- Changing the auth middleware or `GetUserID` helper — these correctly return the Zitadel sub
- Adding caching for the external_id → user.id lookup (premature; single indexed query is sufficient)
- Changing how other RPCs (e.g., User.Create) handle the Zitadel ID — Create already stores it in `external_id`

## Decisions

### D1: Column type TEXT, not BIGINT

Change `users.external_id` from `UUID` to `TEXT` rather than `BIGINT`.

**Rationale**: Although Zitadel IDs are currently numeric, using TEXT avoids coupling to a specific ID format. If Zitadel changes their ID scheme or the project switches identity providers, TEXT accommodates any string-based identifier without further migration. The UNIQUE index on TEXT performs adequately for point lookups.

**Alternative considered**: `BIGINT` — more compact storage and faster comparisons, but assumes Zitadel IDs are always numeric. The Go `Claims.Sub` field is already a `string`, so BIGINT would require parsing.

### D2: ID resolution in use case layer, not interceptor

Add `UserRepository` as a dependency of `ArtistUseCase`. Each artist operation resolves the Zitadel sub to `users.id` via `UserRepository.GetByExternalID()` before calling artist repository methods.

**Rationale**: The use case layer is responsible for orchestrating business logic across repositories. An interceptor approach would query the database on every authenticated request — wasteful for RPCs that don't need the internal ID (e.g., `User.Create`). The use case approach only resolves when needed and avoids the chicken-and-egg problem where `User.Create` is called before the user record exists.

**Alternative considered**: Auth interceptor that injects internal user ID into context — rejected because it would fail for `User.Create` (user doesn't exist yet) and adds unnecessary DB load to every RPC.

### D3: Protobuf external_id validation change

Remove `string.uuid` protovalidate constraint on the `User.external_id` field. Replace with a non-empty string constraint.

**Rationale**: The field no longer holds a UUID. Keeping UUID validation would reject valid Zitadel IDs at the API boundary.

## Risks / Trade-offs

- **UUID → TEXT migration on existing data**: Existing UUID values in `external_id` are valid TEXT strings, so the `ALTER COLUMN TYPE TEXT` is data-compatible and non-destructive. → No data loss risk.
- **Index performance**: TEXT index is marginally slower than UUID index for point lookups. → Negligible at current scale; the column has a UNIQUE constraint which creates a B-tree index.
- **Missing user record**: If `GetByExternalID` returns not-found during an artist operation, the RPC should return `NOT_FOUND` with a clear message. → This indicates the user hasn't completed registration, which is a valid state.

## Migration Plan

1. Create Atlas migration: `ALTER TABLE users ALTER COLUMN external_id TYPE TEXT`
2. Update protobuf `User.external_id` field validation
3. Update `ArtistUseCase` constructor to accept `UserRepository`
4. Update `Follow`, `Unfollow`, `ListFollowed` use case methods to resolve external ID
5. Deploy migration first (backward-compatible), then deploy backend code
