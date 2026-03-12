## Why

Primary key generation is inconsistent across the backend: some tables generate UUIDv7 application-side (artists, venues, events), while others rely on DB DEFAULT (users, tickets, homes). The `homes` table still uses `gen_random_uuid()` (UUIDv4). This prevents deterministic testing, adds unnecessary DB round-trips for `RETURNING id`, and provides no enforcement that IDs are actually UUIDv7. Additionally, the `nullifiers` table has a surrogate `id` column that is never referenced by any code or FK — it should be removed in favor of its natural composite key.

## What Changes

- **DROP DEFAULT** on `id` column for all 8 surrogate-ID tables (`users`, `homes`, `artists`, `artist_official_site`, `venues`, `events`, `tickets`, `push_subscriptions`), forcing application-side generation
- **ADD CHECK constraint** on all surrogate-ID tables to reject non-UUIDv7 values (`substring(id::text, 15, 1) = '7'`)
- **Convert `nullifiers` table** from surrogate PK to composite PK `(event_id, nullifier_hash)` — drop unused `id` column
- **Add entity constructors** (`NewUser`, `NewTicket`, `NewHome`) that generate UUIDv7, matching the existing pattern used by `NewArtist` and `NewVenueFromScraped`
- **Update repository INSERT queries** for `users`, `tickets`, and `homes` to include `id` in the column list instead of relying on `RETURNING id`
- **Remove `id` field** from the nullifier entity and update its repository

## Capabilities

### New Capabilities

_None_

### Modified Capabilities

- `database`: Add requirements for UUIDv7 enforcement (application-side generation, CHECK constraints, no DB DEFAULT on surrogate PKs)
- `artist-auto-persist`: Remove the "Handle artists without MBID" requirement — MBID-less artists are filtered at the use-case layer and the no-MBID INSERT path in the repository becomes dead code after this change

## Impact

- **Backend**: Entity constructors, repository INSERT queries, and nullifier entity/repo changes
- **Database**: Migration to drop defaults, add CHECK constraints, and restructure nullifiers PK
- **Tests**: Integration tests for user/ticket/home creation will need updated setup to provide IDs
- **No Proto changes**: Wire format is unaffected; this is purely an internal enforcement change
- **No Frontend changes**: ID generation is server-side only
