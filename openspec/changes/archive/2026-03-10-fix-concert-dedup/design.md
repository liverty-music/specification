## Context

The `SearchNewConcerts` pipeline has three stages: Gemini API call → application-level dedup → event publish → DB insert. The dedup stage (L2) and the DB insert stage (L4) both fail to prevent duplicates:

- **L2 (getUniqueKey)**: Uses `date + startTime.Format(RFC3339)` as the key. RFC3339 includes the timezone offset, so `18:00:00+09:00` (Gemini) ≠ `09:00:00Z` (pgx readback) even though they represent the same instant. The key also omits the venue name, so distinct concerts at different venues on the same date are incorrectly collapsed.
- **L4 (DB)**: `ON CONFLICT (event_id) DO NOTHING` only protects on the synthetic UUID primary key. Since `CreateFromDiscovered` generates a new UUID per run, every duplicate passes through.

The CronJob runs every ~24h (searchLog TTL), and each run that bypasses dedup adds a full copy of all concerts for every artist. Production data shows 97,041 rows for 484 unique concerts (41 affected artists, ~220 duplicates each).

## Goals / Non-Goals

**Goals:**

- Fix the application-level dedup key to use `(local_event_date, listed_venue_name, start_at_utc)` with correct nil-handling.
- Add a DB-level UNIQUE constraint as a final safety net.
- Change INSERT to UPSERT so newly discovered `start_at` values update existing records.
- Clean up the 97,041 duplicate rows in a migration.

**Non-Goals:**

- Fuzzy venue name matching (e.g., "Zepp Tokyo" vs "Zepp東京"). Exact string match is sufficient; the venue normalization pipeline handles canonical name resolution separately.
- Changing the CronJob schedule or searchLog TTL.
- Modifying the `concert.discovered.v1` event schema or the Watermill messaging pipeline.

## Decisions

### Decision 1: New dedup key — `(local_event_date, listed_venue_name, start_at_utc)`

**Choice**: Replace `getUniqueKey(date, startTime)` with a new function that includes `listed_venue_name` and normalizes `startTime` to UTC before formatting.

**Rationale**: The venue name is the most stable identifier from Gemini — it rarely varies across runs for the same concert. Adding it to the key simultaneously fixes two bugs: (a) same-venue/same-date concerts are no longer differentiated only by an unreliable `startTime`, and (b) different-venue concerts on the same date are no longer incorrectly collapsed.

**Alternatives considered**:
- `(date, title)`: Titles vary too much across Gemini runs (trailing whitespace, subtitle changes).
- `(date, venue)` only: Would collapse matinee/evening shows at the same venue. Adding UTC-normalized `start_at` preserves these.

### Decision 2: Nil start_at comparison semantics

**Choice**: When the scraped `start_at` is nil, treat it as a wildcard that matches any existing `start_at` at the same (date, venue). When the existing `start_at` is nil and scraped is non-nil, publish for UPSERT update.

**Rationale**: Gemini's inability to extract `start_at` in one run does not mean the concert is different. The information asymmetry is one-directional: nil → "I don't know" (match any), non-nil → "I know this" (new info to persist).

**Implementation**: The `seen` map key format will be `"YYYY-MM-DD|venue_name|HH:MM:SSZ"` when `start_at` is non-nil (UTC-normalized), or `"YYYY-MM-DD|venue_name"` (no start_at segment) when nil. Lookup logic:
1. Build `seen` set from existing concerts with their full keys.
2. Also build a `seenDateVenue` set with just `"YYYY-MM-DD|venue_name"` for nil-match.
3. For each scraped concert:
   - If scraped `start_at` is nil → check `seenDateVenue` → if hit, skip (dedup).
   - If scraped `start_at` is non-nil → check `seen` with full UTC key → if hit, skip.
   - If scraped `start_at` is non-nil → check `seenDateVenue` for existing nil records → if hit AND existing had nil start_at, publish (UPSERT will fill start_at).
   - Otherwise → publish (genuinely new).

### Decision 3: DB UNIQUE constraint with NULLS NOT DISTINCT

**Choice**: Add `UNIQUE NULLS NOT DISTINCT (venue_id, local_event_date, start_at)` on the `events` table.

**Rationale**: PostgreSQL 15+ supports `NULLS NOT DISTINCT`, which treats two NULL `start_at` values as equal for uniqueness purposes. This matches our business rule: two events at the same venue on the same date with unknown start times are the same event.

**Why `venue_id` instead of `listed_venue_name`**: The DB constraint uses the normalized `venue_id` FK (already resolved during `CreateFromDiscovered`), not the raw text. Multiple raw names can map to the same venue (e.g., "Zepp Tokyo" and "Zepp 東京" after normalization). Using `venue_id` provides stronger uniqueness.

### Decision 4: UPSERT with COALESCE for time fields

**Choice**: Change `ON CONFLICT DO NOTHING` to `ON CONFLICT (venue_id, local_event_date, start_at) DO UPDATE SET start_at = COALESCE(EXCLUDED.start_at, events.start_at), open_at = COALESCE(EXCLUDED.open_at, events.open_at)`.

**Rationale**: COALESCE ensures that non-NULL values are never overwritten by NULL (Gemini regression), while previously-NULL fields are updated when new information arrives.

### Decision 5: Cleanup migration — delete-then-constrain

**Choice**: A single migration that (1) deletes duplicate rows keeping the richest/earliest per natural key, then (2) adds the UNIQUE constraint.

**Rationale**: The constraint cannot be added while duplicates exist. Performing both in one migration ensures atomicity — if the constraint fails, the transaction rolls back and no data is lost.

## Risks / Trade-offs

- **[Risk] Matinee/evening shows with start_at=nil**: If both shows are first scraped without start_at, only one row will exist (nil+nil dedup). When Gemini later returns start_at for the second show, the UPSERT will update the existing row rather than creating a new one. → **Mitigation**: This is an acceptable data loss for a very rare edge case. The next CronJob run will discover the second show with a distinct start_at and insert it as a new row.

- **[Risk] Venue name mismatch between runs**: If Gemini returns "Zepp Tokyo" in one run and "ZEPP TOKYO" in another, the application-level dedup will treat them as different venues. → **Mitigation**: The DB constraint uses `venue_id` (post-normalization), so the DB layer catches this. The duplicate will be silently skipped by the UPSERT.

- **[Risk] Migration on 97K rows**: The cleanup DELETE may lock the `events` table briefly. → **Mitigation**: The `events` table is only written by the consumer process (async), not by user-facing RPCs. A brief lock during migration is acceptable for the dev environment. For production, the migration runs via Atlas Operator before the backend deployment starts.

## Migration Plan

1. **Generate migration**: `atlas migrate diff --env local fix_concert_dedup`
2. **Local validation**: Apply locally, verify row count drops from ~97K to ~484.
3. **Deploy order**: Migration runs first (Atlas Operator sync wave), then new backend code deploys.
4. **Rollback**: The UNIQUE constraint can be dropped and the migration reverted. Deleted duplicate data is not recoverable but is fully reproducible by re-running the CronJob.

## Open Questions

(none)
