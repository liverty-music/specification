## Context

The Gemini-based concert searcher extracts venue names as free-text strings (e.g., "日本武道館", "Nippon Budokan", "武道館"). These are stored directly as `venues.name` and used as the deduplication key via exact-match `GetByName`. Because the same physical venue can appear under multiple spellings across different artist pages or scrape runs, duplicate venue records accumulate in the database. Once PR #45 (extract-concert-venue) ships, `events.listed_venue_name` will preserve the original Gemini text, but `venues.name` continues to be used for deduplication — the core problem remains.

This change introduces an async enrichment pipeline that resolves raw venue names to external canonical identities (MusicBrainz MBID or Google Maps place_id) and merges duplicate records.

## Goals / Non-Goals

**Goals:**
- Resolve venue names to canonical external IDs (MusicBrainz MBID or Google Maps place_id)
- Update `venues.name` to the canonical name provided by the external source
- Detect and merge duplicate venue records sharing the same external ID
- Track enrichment state per venue via `enrichment_status` enum
- Extend the existing MusicBrainz client with `place` endpoint support

**Non-Goals:**
- Exposing `mbid` / `google_place_id` in the public API (future change)
- Rate-limit management for external APIs (noted as TODO — existing MusicBrainz throttler reused as-is)
- Migrating job trigger to event-driven architecture (future follow-up)
- Running a dedicated backfill migration script — existing rows receive `enrichment_status = 'pending'` via the column default and will be processed organically on the next scheduled job run

## Decisions

### D1: MusicBrainz first, Google Maps as fallback

MusicBrainz is free and open, and its `place` entity includes alias records (e.g., "Nippon Budokan", "日本武道館", "武道館" all resolve to the same MBID). The existing codebase already has a MusicBrainz client and throttler. Google Maps has superior coverage for smaller venues but incurs per-request cost. The sequential strategy avoids unnecessary Maps API calls.

**Alternatives considered:**
- Google Maps only: Better coverage, but cost scales with venue volume and vendor lock-in.
- Parallel lookup: Reduces latency but doubles cost on every request regardless of MB hit rate.

### D2: `enrichment_status` enum with three states (`pending`, `enriched`, `failed`)

A dedicated status column enables targeted queries (`WHERE enrichment_status = 'pending'`) and prevents the job from retrying permanently unresolvable venues (small live houses not in either database). `failed` makes the unresolvable set visible for future manual review or alternative strategies.

**Alternatives considered:**
- `mbid IS NULL AND google_place_id IS NULL` as implicit "pending": Works but conflates "not yet tried" with "tried and failed". Prevents safe retry logic.
- `enrichment_attempted_at TIMESTAMPTZ`: More flexible for time-based retry, but adds complexity not needed now. Can be added later.

### D3: Duplicate detection during enrichment (single pass)

When the enrichment job resolves a venue to a canonical ID, it immediately checks for an existing venue record with the same ID. If found, it merges within the same transaction. This avoids a separate reconciliation pass and ensures duplicate records never remain in the DB longer than necessary.

**Merge rules:**
- Canonical venue: the record with the older `created_at` (first-seen wins)
- `events.venue_id` references updated to point to canonical
- `admin_area`: `COALESCE(canonical.admin_area, duplicate.admin_area)` — preserve any non-NULL value
- Canonical `venues.name` updated to external canonical name; duplicate deleted

### D4: Job piggybacks on `concert-discovery` CronJob

Venue enrichment runs as a post-step in the existing `concert-discovery` job binary, after all artists have been processed. This avoids deploying a new CronJob resource and leverages already-initialized dependencies (DB, MusicBrainz client). A follow-up change will migrate to event-driven triggering once concert-search supports user-Follow-triggered execution.

### D5: `admin_area` as search hint for external APIs

When calling MusicBrainz or Google Maps, the job includes `venues.admin_area` (set by PR #45) in the search query if non-NULL. This improves match accuracy for venues with common names (e.g., "Zepp Nagoya" in "愛知県" vs other "Zepp" venues).

### D6: `raw_name` column to preserve original scraper-provided venue name

When the enrichment pipeline overwrites `venues.name` with the canonical name (e.g., "Nippon Budokan"), the original scraper-provided name (e.g., "日本武道館") must be preserved for deduplication. Without this, the next scrape providing the same raw name would fail `GetByName` and create a new duplicate — leading to an infinite create-merge cycle. The `raw_name` column stores the original name before the first enrichment overwrite, and `GetByName` falls back to matching on `raw_name` when no `name` match is found.

**Alternatives considered:**
- Alias table (`venue_aliases`): More flexible for venues with many alternate names, but adds complexity (new table, new queries) beyond what's needed now. Can be added later if a single `raw_name` proves insufficient.
- Skip name overwrite: Loses the benefit of canonical naming. The whole point of enrichment is normalizing venue names.

## Risks / Trade-offs

- **MusicBrainz coverage gaps** → Smaller Japanese live houses may not be registered. Mitigated by Google Maps fallback. Remaining `failed` venues are acceptable and visible.
- **Google Maps cost at scale** → Only triggered after MB miss. Cost is bounded by the number of venues not in MusicBrainz. Rate-limit strategy deferred as TODO.
- **Merge touching `events` table** → UPDATE on `events.venue_id` could be a large write if a duplicate venue has many events. Mitigated by running in a transaction; no user-facing downtime expected at current data volumes.
- **`enrichment_status = 'pending'` for all pre-existing venues** → Existing venues will be enriched on the next job run. No immediate behavioral change; `venues.name` remains valid for `GetByName` until overwritten.

## Migration Plan

1. Deploy Go changes (entity, usecase, enrichment job step — all additive)
2. Run migration:
   ```sql
   CREATE TYPE venue_enrichment_status AS ENUM ('pending', 'enriched', 'failed');
   ALTER TABLE venues
     ADD COLUMN mbid TEXT,
     ADD COLUMN google_place_id TEXT,
     ADD COLUMN enrichment_status venue_enrichment_status NOT NULL DEFAULT 'pending',
     ADD COLUMN raw_name TEXT;
   UPDATE venues SET raw_name = name;
   CREATE UNIQUE INDEX idx_venues_mbid ON venues (mbid) WHERE mbid IS NOT NULL;
   CREATE UNIQUE INDEX idx_venues_google_place_id ON venues (google_place_id) WHERE google_place_id IS NOT NULL;
   ```
3. Enrichment runs automatically on the next concert-discovery CronJob execution
4. Rollback: drop the columns, indexes, and the enum type (no data loss beyond new fields)

## Open Questions

- **Rate limiting for Google Maps**: What is the acceptable quota per job run? *(deferred as TODO)*
- **Future event-driven trigger**: When concert-search supports Follow-triggered execution, venue enrichment should be triggered immediately after a new venue is created rather than waiting for the next cron cycle.
