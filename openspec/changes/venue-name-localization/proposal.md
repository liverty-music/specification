## Why

Concert venue names are displayed in English regardless of the user's preferred language because the Google Places API is called without a `languageCode` parameter, causing English canonical names (e.g., "Nippon Budokan") to be stored and surfaced — even though the Gemini scraper already captures the correct Japanese names in `listed_venue_name`. Users with a Japanese preference see English venue names on event cards and detail sheets.

## What Changes

- The Google Places API `SearchPlace` call will include a `languageCode` derived from the venue's country code (extracted from `admin_area`, e.g. `"JP-13"` → `"ja"`), so newly resolved venues are stored with locale-appropriate canonical names.
- `listed_venue_name` will be normalized (prefecture prefixes stripped) before being stored in `staged_concerts`, so the frontend can use it as a clean display value.
- The frontend concert mapper will select the venue name based on the user's current language: prefer `listed_venue_name` for `ja`, prefer `venue.name` for `en`, with cross-fallback.

## Capabilities

### New Capabilities

- `venue-name-localization`: Locale-aware venue name display — how the frontend selects between `listed_venue_name` and `venue.name` based on `currentLanguage`, and the fallback chain when either field is absent.

### Modified Capabilities

- `venue-normalization`: Two new requirements — (1) the Places API call MUST include a `languageCode` derived from the venue's country code; (2) `listed_venue_name` MUST be normalized via `NormalizeVenueName` before being persisted to `staged_concerts`.

## Impact

- **Backend**: `internal/infrastructure/maps/google/client.go` (add `languageCode` to Places request), `internal/usecase/concert_creation_uc.go` (normalize `listed_venue_name` before storage), new helper function for country-code → language-code mapping.
- **Frontend**: `src/adapter/rpc/mapper/concert-mapper.ts` (locale-aware `venueName` selection), caller sites that instantiate or invoke the mapper must pass `currentLanguage`.
- **No schema change**: existing proto fields (`venue.name`, `listed_venue_name`) are sufficient; no BSR gen cycle required.
- **Existing venues**: venues already stored with English canonical names are covered by the frontend fallback to `listed_venue_name`. Venues without `listed_venue_name` will remain in English until re-resolved.
