## Why

The guest onboarding UX has three compounding issues: the artist-filter UI clutters the header with redundant artist names; laser beam effects (a core "wow" moment) never render for guest users because `GuestFollow` lacks a `hype` field, causing all events to fall back to `hype='watch'` which never satisfies `isHypeMatched`; and the signup banner carries inconsistent copy across locales. All three are visible immediately after onboarding completes and undermine first impressions.

## What Changes

- **Remove filter chips from page header** — artist names SHALL NOT be rendered as chips in the header when a filter is active; the filter icon's active state (color change via `data-active`) alone conveys filter status; dismiss is achieved by re-tapping the filter icon to open the bottom sheet
- **Eliminate `GuestFollow` entity** — replace `GuestFollow` with `FollowedArtist` as the unified follow representation for both guest and authenticated users; hype is stored inline alongside artist data rather than in a separate `hypes: Record<string, string>` sidecar; `DEFAULT_HYPE` constant defined in entity layer
- **Fix guest laser beam rendering** — `FollowServiceClient.listFollowed()` for unauthenticated users SHALL read persisted hype from `GuestService` instead of hardcoding `'watch'`; matched events will render beam effects correctly
- **Align signup banner copy** — Japanese banner message shortened to ≤2 lines; English message updated to match intent

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `dashboard-artist-filter`: Remove the "filter chips displayed in header" requirement; filter active state conveyed by icon styling only
- `signup-prompt-banner`: Update banner copy requirement to reflect new Japanese text (≤2 lines) and aligned English text
- `guest-data-merge`: `GuestFollow` storage format changes — follows are stored as `FollowedArtist[]` (with `hype` field) under a single key; separate `liverty:guest:hypes` key is eliminated; migration path required for existing localStorage data

## Impact

- `frontend/src/entities/follow.ts` — remove `GuestFollow`, add `DEFAULT_HYPE` constant
- `frontend/src/adapter/storage/guest-storage.ts` — remove `saveHypes`/`loadHypes`/`clearHypes`; update `saveFollows`/`loadFollows` to use `FollowedArtist[]`; update validator to include `hype` field (with fallback for legacy data)
- `frontend/src/services/guest-service.ts` — `follows` typed as `FollowedArtist[]`; remove `hypes` sidecar; `setHype()` updates the matching follow entry; `getHypes()` removed
- `frontend/src/services/follow-service-client.ts` — `listFollowed()` guest branch returns `guest.follows` directly (already typed as `FollowedArtist[]`)
- `frontend/src/components/artist-filter-bar/artist-filter-bar.html` — remove chips `<ul>` block (lines 18–32)
- `frontend/src/locales/en/translation.json` and `ja/translation.json` — update `myArtists.signupBanner.message`
- `frontend/src/entities/index.ts` — remove `GuestFollow` re-export
- No backend changes; no proto changes; no BSR release needed
