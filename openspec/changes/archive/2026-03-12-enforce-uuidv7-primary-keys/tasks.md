## 1. Database Migration

- [x] 1.1 Create migration: DELETE orphaned artists with NULL MBID
- [x] 1.2 Create migration: ALTER `artists.mbid` SET NOT NULL
- [x] 1.3 Create migration: Replace partial unique index on `artists.mbid` with a full unique index (remove WHERE clause)
- [x] 1.4 Create migration: DROP DEFAULT on `id` column for all 8 surrogate-ID tables (`users`, `homes`, `artists`, `artist_official_site`, `venues`, `events`, `tickets`, `push_subscriptions`)
- [x] 1.5 Create migration: ADD CHECK constraint `chk_<table>_id_uuidv7` on all 8 tables
- [x] 1.6 Create migration: Convert `nullifiers` table — drop `id` column, drop `idx_nullifiers_event_hash`, add composite PK `(event_id, nullifier_hash)`
- [x] 1.7 Update `schema.sql` desired state to reflect all migration changes
- [x] 1.8 Add new migration file to `k8s/atlas/base/kustomization.yaml` under `configMapGenerator.files`

## 2. Entity Layer

- [x] 2.1 Move `newID()` helper from `entity/artist.go` to a shared `entity/id.go` file
- [x] 2.2 Add `NewUser()` constructor in `entity/user.go` that generates UUIDv7
- [x] 2.3 Add `NewTicket()` constructor in `entity/ticket.go` that generates UUIDv7
- [x] 2.4 Add `NewHome()` constructor in `entity/user.go` (or separate file) that generates UUIDv7
- [x] 2.5 Remove `ID` field from nullifier entity (if it exists as a struct)

## 3. Repository Layer

- [x] 3.1 Update `user_repo.go`: include `id` in users INSERT query, remove `RETURNING id`, use constructor-provided ID
- [x] 3.2 Update `user_repo.go`: include `id` in homes INSERT/UPSERT query, remove `RETURNING id`
- [x] 3.3 Update `ticket_repo.go`: include `id` in tickets INSERT query, change `RETURNING id, minted_at` to `RETURNING minted_at`
- [x] 3.4 Update `nullifier_repo.go`: remove any references to `id` field
- [x] 3.5 Remove `insertArtistsNoMBIDUnnestQuery` and its branching logic from `artist_repo.go`
- [x] 3.6 Update `ArtistRepository.Create()` to require non-empty MBID for all artists

## 4. Use Case Layer

- [x] 4.1 Update `artistUseCase.Create()` to reject artists without MBID (change validation from `name == "" && mbid == ""` to require MBID)
- [x] 4.2 Update callers of user/ticket/home creation to use new constructors

## 5. Tests

- [x] 5.1 Update artist repo integration tests for MBID NOT NULL enforcement
- [x] 5.2 Update user repo integration tests to provide app-generated IDs
- [x] 5.3 Update ticket repo integration tests to provide app-generated IDs
- [x] 5.4 Update nullifier repo integration tests for composite PK
- [x] 5.5 Add entity unit tests for new constructors (`NewUser`, `NewTicket`, `NewHome`)
- [x] 5.6 Run `make check` to verify all tests pass and lints are clean
