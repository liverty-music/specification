## Context

The Gemini-based concert searcher currently extracts 6 fields per event (artist name, event name, venue, date, start time, source URL). The `venue` field is a raw text string (e.g., "Zepp Osaka Bayside") that is stored as `venues.name` and used as the deduplication key for venue lookup/creation.

Two gaps block the upcoming location-based dashboard feature:

1. **No geographic area on the venue** — there is no way to associate a concert with a prefecture or state to power the "My City" / "My Region" lane filtering.
2. **Raw venue name lost after processing** — once the venue is matched/created by name, the original scraped text is discarded. This prevents future normalization workflows (e.g., matching against Google Maps or MusicBrainz to get a canonical name).

## Goals / Non-Goals

**Goals:**
- Extend Gemini extraction to return `admin_area` (都道府県-level administrative division)
- Persist `admin_area` on the `venues` table
- Preserve the raw scraped venue name as `listed_venue_name` on the `events` table
- Rename `ScrapedConcert.VenueName` → `ListedVenueName` throughout the pipeline for semantic clarity

**Non-Goals:**
- Normalization of venue names via Google Maps / MusicBrainz (future change)
- Making `venues.name` nullable (deferred to normalization change)
- Filtering concerts by `admin_area` in the API (separate frontend change)
- User `admin_area` profile field (separate onboarding change)

## Decisions

### D1: Field name `AdminArea` over `Prefecture`

`Prefecture` is Japan-specific. `AdminArea` maps to `administrative_area_level_1` in the Google Maps Geocoding API and works equally for US states, Canadian provinces, German Bundesländer, etc. Chosen for international extensibility.

**Alternatives considered:**
- `Prefecture`: Semantically precise for Japan MVP, but a breaking rename when internationalizing.
- `Region`: Conflicts with the dashboard's "地方" concept (a grouping of prefectures), which is derived — not stored — at the application layer.
- `State`/`Province`: Country-specific terminology; not universal.

### D2: `admin_area` is nullable (`*string` in Go, `TEXT` in Postgres)

Gemini cannot always determine the venue's location with confidence. The extraction rule is: populate only when explicitly stated or unambiguously inferable from the venue name or page context; otherwise return empty string (stored as `NULL`). A wrong value is strictly worse than `NULL`, since it would silently misroute concerts in the dashboard.

### D3: `ListedVenueName` lives on `Event`, not `Venue`

The listed name is tied to a specific source/scrape — two sources might list the same venue differently ("Zepp Osaka" vs "Zepp Osaka Bayside"). It is a property of the *event occurrence* (how it was advertised), not of the venue entity itself. Storing it on `events` preserves provenance and enables future normalization without altering the venue deduplication key.

### D4: `venues.name` stays `NOT NULL` for this change

`Venue.Name` currently holds the listed name and acts as the deduplication key in `GetByName`. Making it nullable now would require null-safe SQL comparisons and nil-checks throughout the codebase without delivering any feature value. When the normalization change arrives, it will introduce a dedicated `listed_name NOT NULL` column for lookups and make `name` nullable via a separate migration.

### D5: Gemini prompt uses "confident or empty" framing

The prompt instructs Gemini: populate `admin_area` only when explicitly stated or clearly inferable from the venue name (e.g., "Zepp Nagoya" → "愛知県"); return `""` if there is any ambiguity. The `eventSchema` marks `admin_area` as optional (not in `Required` array) so the model can omit it cleanly.

## Risks / Trade-offs

- **Gemini hallucination on ambiguous venues** → Mitigated by strict prompt wording ("wrong value is worse than empty") and nullable storage. Dashboard filtering treats NULL as "unknown" and places the concert in the "Others" lane.
- **Existing venue records have no `admin_area`** → The `admin_area` column is `NULL` for all existing rows. Acceptable: no existing venue data exists in production at this stage.
- **`listed_venue_name` is NULL for pre-migration concert records** → Column is nullable; historical rows are unaffected. New rows always carry the value.
- **`VenueName` → `ListedVenueName` rename is a breaking change in test fixtures** → All occurrences in `concert_uc_test.go` and `searcher_test.go` must be updated. Low risk (internal, no API surface change).

## Migration Plan

1. Deploy Go changes (entity, usecase, gemini, repo — backward-compatible until migration runs)
2. Run migration: `ALTER TABLE venues ADD COLUMN admin_area TEXT` and `ALTER TABLE events ADD COLUMN listed_venue_name TEXT`
3. New concert discoveries automatically populate both columns going forward
4. Rollback: drop the two columns (no data loss beyond the new fields)

## Open Questions

_(none — all design decisions resolved in exploration phase)_
