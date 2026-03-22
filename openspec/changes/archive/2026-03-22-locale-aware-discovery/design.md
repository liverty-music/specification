## Context

The Discovery page (used in both onboarding and the Discover tab) calls `ArtistService.ListTop` with a hardcoded `country = 'Japan'`. This means non-Japanese users see Japan-centric results. Additionally, when a genre tag is selected, the backend delegates to Last.fm's `tag.getTopArtists` endpoint, which has no country parameter — results are always global for that genre.

The user's home area (`UserHomeSelector`) is only presented on the Dashboard (Step 3), after Discovery (Step 1). During onboarding discovery, there is no user home to reference.

The browser's `Intl.DateTimeFormat().resolvedOptions().timeZone` API returns the OS timezone synchronously without requiring any permission prompt. This can be mapped to a country name for the `ListTop` call.

## Goals / Non-Goals

**Goals:**
- Dynamically detect the user's country from browser timezone and use it for `ListTop` calls
- Remove all hardcoded `'Japan'` country values from the Discovery page
- Document the `tag` vs `country` priority logic in the `ListTopRequest` proto comments
- Graceful fallback to global chart when country cannot be determined

**Non-Goals:**
- Combining tag + country filtering (Last.fm API does not support this)
- Using `navigator.geolocation` (requires permission prompt, async)
- Moving `UserHomeSelector` earlier in the onboarding flow
- Backend changes (already accepts dynamic country)

## Decisions

### 1. Country detection via `Intl.DateTimeFormat().resolvedOptions().timeZone`

Use the IANA timezone identifier to infer the user's country. This is synchronous, requires no permission, and is available in all modern browsers.

**Alternatives considered:**
- `navigator.language` — Returns language preference, not location. `en` doesn't imply a country.
- `navigator.geolocation` — Requires permission prompt, async, overkill for country-level granularity.
- Move `UserHomeSelector` before Discovery — Adds onboarding friction for a problem solvable without user interaction.

### 2. Static timezone-to-country mapping table

Maintain a curated mapping of IANA timezone → ISO 3166-1 country name (as Last.fm expects). The table covers major timezones (~40 entries for countries with active Last.fm data). Unknown timezones fall back to empty string → global chart.

**Alternatives considered:**
- Full IANA database (~400+ entries) — Over-engineered. Most timezones map to countries with negligible Last.fm data.
- Third-party library (e.g., `countries-and-timezones`) — Unnecessary dependency for a simple lookup table.

### 3. Genre selection returns global results (by design)

When a genre chip is tapped, `tag.getTopArtists` returns global results for that genre. This is a Last.fm API limitation, not a bug. The proto comments will document this explicitly so callers understand the behavior.

When the genre is deselected, the system reverts to `geo.getTopArtists` with the detected country.

### 4. Proto comment clarification (no wire changes)

Update `ListTopRequest` field comments and the `ListTop` RPC comment to document the data-source priority:
1. `tag` set → `tag.getTopArtists` (global, country ignored)
2. `tag` empty, `country` set → `geo.getTopArtists` (regional)
3. Both empty → `chart.getTopArtists` (global)

This is a comment-only change — no breaking changes, no field additions.

## Risks / Trade-offs

- **Timezone ≠ location**: VPN users or users with misconfigured OS timezone get wrong country → Acceptable. Fallback is global chart, not broken behavior.
- **Sparse mapping table**: Countries not in the mapping get global results → Better than hardcoded Japan for everyone. Table can be expanded incrementally.
- **Genre results are global**: Users may expect "Rock in Japan" but get "Rock globally" → Document in UI or accept as-is. Last.fm API constraint.
- **Cache interaction**: Backend caches by `country+tag+limit`. Changing from hardcoded `'Japan'` to dynamic countries increases cache cardinality → Minimal impact; cache is in-memory and short-lived.
