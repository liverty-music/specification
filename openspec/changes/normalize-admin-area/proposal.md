## Why

Venue `admin_area` is currently stored as free-text Japanese strings ("東京", "愛知県") with inconsistent suffixes. This prevents future internationalization, causes fragile string normalization in the frontend (`s.replace(/[県都道府]$/, '')`), and blocks the planned user home area feature from using a stable identifier for lane assignment. Additionally, the user's geographic preference is only persisted in localStorage—losing it on device switch, preventing server-side use, and making the data inaccessible to guests who later sign up.

The user's home area also needs to be extensible: a flat ISO 3166-2 string is sufficient for Japan (prefecture-level), but future US expansion may require county-level granularity. The data model should support this without a breaking migration.

## What Changes

- **Adopt ISO 3166-2 codes** (e.g., `JP-13`, `JP-40`) as the canonical representation for `Venue.admin_area` across DB, Proto, and API layers.
- **Add a backend normalization function** that converts Gemini's free-text admin_area output (e.g., "東京", "東京都", "Aichi") into the corresponding ISO 3166-2 code before persistence. Unrecognized values become NULL.
- **Introduce structured `User.home`** — a new proto message with `country_code` (ISO 3166-1), `level_1` (ISO 3166-2 subdivision), and optional `level_2` (country-specific finer area). Stored in a normalized `homes` table, referenced from `users.home_id`.
- **Include optional `home` in `CreateRequest`** so the area selected during onboarding is persisted atomically with account creation, eliminating the need for a separate `UpdateHome` call after sign-up.
- **Replace localStorage-based region storage** with RPC calls to `UserService.Create` (with home) / `UserService.UpdateHome` / reading `User.home` from the `Get` response.
- **Rename dashboard lanes** from `main / region / other` to `home / nearby / away` to reflect the new domain language.
- **Migrate existing data**: convert existing free-text `venues.admin_area` values to ISO 3166-2 codes; migrate existing `users.home` text column to `homes` table records.

## Capabilities

### New Capabilities
- `user-home`: Structured user home area selection, persistence via Create and UpdateHome RPCs, and retrieval. Covers the `Home` proto message, `homes` DB table, `UserService` RPC changes, and frontend integration.
- `admin-area-normalization`: Backend normalization function that maps free-text administrative area strings to ISO 3166-2 codes. Used by the concert discovery pipeline post-Gemini extraction.

### Modified Capabilities
- `venue-normalization`: `admin_area` value changes from free-text to ISO 3166-2 code; search hint logic must convert code back to locale text before querying MusicBrainz/Google Maps.
- `localstorage-naming`: Remove `user.adminArea` and `guest.adminArea` keys; geographic preference moves to server-side `User.home`.
- `live-events`: Dashboard lane assignment changes from `main/region/other` to `home/nearby/away`; comparison logic uses structured Home with level-aware granularity.

## Impact

- **Proto** (`specification`): Restructured `Home` message with `country_code`, `level_1`, `level_2`; optional `home` added to `CreateRequest`; `UpdateHome` RPC updated for structured Home; `AdminArea` description updated to specify ISO 3166-2.
- **Backend** (`backend`): New normalization package; `User` entity gains structured `Home` field; new `homes` table and repository; `UserRepository` gains `UpdateHome`; `Create` handler accepts optional home; Gemini pipeline post-processing updated; venue enrichment search hint needs code-to-text conversion.
- **Frontend** (`frontend`): Create RPC includes home from onboarding; region setup sheet stores via RPC instead of localStorage; dashboard lane logic renamed and level-aware; `StorageKeys` entries for adminArea removed; display layer converts ISO code to localized name.
- **Database**: New `homes` table; `users.home_id` FK replaces `users.home` text column; migration to convert existing `venues.admin_area` free-text to ISO 3166-2 codes.
