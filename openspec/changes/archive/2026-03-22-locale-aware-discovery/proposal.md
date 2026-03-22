## Why

The Discovery page hardcodes `country = 'Japan'` when calling `ArtistService.ListTop`. Users outside Japan see Japanese regional top artists instead of artists relevant to their location. Additionally, when a genre tag is selected, the backend uses `tag.getTopArtists` (Last.fm) which has no country parameter — so results are always global regardless of the country value passed. The `ListTopRequest` proto comments do not document this priority logic, making it easy for callers to assume both fields work together.

## What Changes

- **Browser locale detection**: Infer the user's country from `Intl.DateTimeFormat().resolvedOptions().timeZone` (no permission prompt required) and use it as the default country for `ListTop` calls on the Discovery page.
- **Remove hardcoded `'Japan'`**: Replace all hardcoded country values in `genre-filter-controller.ts`, `bubble-manager.ts`, and `discovery-route.ts` with the dynamically detected country.
- **Fallback to global chart**: When timezone-to-country mapping fails (e.g., `"UTC"`, `"Etc/GMT+9"`), pass empty country to get global results.
- **Document ListTop priority logic in proto**: Add comments to `ListTopRequest` clarifying that `tag` and `country` are mutually exclusive at the data-source level — when `tag` is set, country is ignored and results are global for that genre.

## Capabilities

### New Capabilities

- `browser-locale-detection`: Timezone-based country detection utility for determining user's country from browser environment without requiring geolocation permission.

### Modified Capabilities

- `bubble-pool-lifecycle`: Initial pool load uses detected country instead of hardcoded `'Japan'`. Genre filtering behavior unchanged (global results by design).
- `discover`: Genre filtering on Discover tab uses detected country for initial load; genre chip selection returns global genre results (documented behavior).

## Impact

- **Proto** (`artist_service.proto`): Comment-only change on `ListTopRequest` — no wire-breaking changes.
- **Frontend** (`discovery-route.ts`, `genre-filter-controller.ts`, `bubble-manager.ts`): Replace hardcoded country with dynamic detection.
- **Frontend** (new utility): Timezone-to-country mapping module.
- **Backend**: No changes required — already accepts dynamic country parameter.
- **Tests**: Frontend unit tests that mock `'Japan'` country need updating.
