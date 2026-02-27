## Why

Venue `admin_area` is currently stored as free-text Japanese strings ("東京", "愛知県") with inconsistent suffixes. This prevents future internationalization, causes fragile string normalization in the frontend (`s.replace(/[県都道府]$/, '')`), and blocks the planned user home area feature from using a stable identifier for lane assignment. Additionally, the user's geographic preference is only persisted in localStorage—losing it on device switch, preventing server-side use, and making the data inaccessible to guests who later sign up.

## What Changes

- **Adopt ISO 3166-2 codes** (e.g., `JP-13`, `JP-40`) as the canonical representation for `Venue.admin_area` across DB, Proto, and API layers.
- **Add a backend normalization function** that converts Gemini's free-text admin_area output (e.g., "東京", "東京都", "Aichi") into the corresponding ISO 3166-2 code before persistence. Unrecognized values become NULL.
- **Introduce `User.home`** — a new field on the User entity representing the user's home area (ISO 3166-2 code), persisted in the database and exposed via `UserService` RPCs.
- **Replace localStorage-based region storage** with RPC calls to `UserService.UpdateHome` / reading `User.home` from the `Get` response.
- **Rename dashboard lanes** from `main / region / other` to `home / nearby / away` to reflect the new domain language.
- **Migrate existing data**: convert existing free-text `venues.admin_area` values to ISO 3166-2 codes via a database migration.

## Capabilities

### New Capabilities
- `user-home`: User home area selection, persistence via RPC, and retrieval. Covers the `User.home` field, `UserService.UpdateHome` RPC, DB migration, and frontend integration.
- `admin-area-normalization`: Backend normalization function that maps free-text administrative area strings to ISO 3166-2 codes. Used by the concert discovery pipeline post-Gemini extraction.

### Modified Capabilities
- `venue-normalization`: `admin_area` value changes from free-text to ISO 3166-2 code; search hint logic must convert code back to locale text before querying MusicBrainz/Google Maps.
- `localstorage-naming`: Remove `user.adminArea` and `guest.adminArea` keys; geographic preference moves to server-side `User.home`.
- `live-events`: Dashboard lane assignment changes from `main/region/other` to `home/nearby/away`; comparison logic uses ISO 3166-2 codes instead of normalized Japanese strings.

## Impact

- **Proto** (`specification`): New `Home` message in `user.proto`; new `UpdateHome` RPC in `user_service.proto`; `AdminArea` description updated to specify ISO 3166-2.
- **Backend** (`backend`): New normalization package; `User` entity gains `Home` field; `UserRepository` gains `UpdateHome`; Gemini pipeline post-processing updated; venue enrichment search hint needs code-to-text conversion.
- **Frontend** (`frontend`): Region setup sheet stores via RPC instead of localStorage; dashboard lane logic renamed; `StorageKeys` entries for adminArea removed; display layer converts ISO code to localized name.
- **Database**: Migration to add `home` column to `users` table; migration to convert existing `venues.admin_area` free-text to ISO 3166-2 codes.
