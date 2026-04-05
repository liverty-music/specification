## 1. Entity Layer — Unify Follow Representation

- [x] 1.1 Add `DEFAULT_HYPE: Hype = 'watch'` constant to `src/entities/follow.ts`
- [x] 1.2 Remove `GuestFollow` interface from `src/entities/follow.ts`
- [x] 1.3 Remove `GuestFollow` from `src/entities/index.ts` re-exports

## 2. Storage Adapter — Unified Follow Format

- [x] 2.1 Update `saveFollows` / `loadFollows` in `src/adapter/storage/guest-storage.ts` to use `FollowedArtist[]`
- [x] 2.2 Update `isGuestFollow` validator to check for `hype` field; fall back to `DEFAULT_HYPE` when field is absent (legacy migration)
- [x] 2.3 Remove `saveHypes`, `loadHypes`, `clearHypes` functions from `src/adapter/storage/guest-storage.ts`

## 3. GuestService — Inline Hype Management

- [x] 3.1 Change `follows` field type to `FollowedArtist[]` in `src/services/guest-service.ts`; update `loadFollows()` call
- [x] 3.2 Remove `hypes: Record<string, string>` field and `loadHypes()` initialization
- [x] 3.3 Rewrite `setHype(artistId, hype)` to mutate the matching `follows` entry and call `persistFollows()`
- [x] 3.4 Remove `getHypes()` method
- [x] 3.5 Update `follow()` to push `{ artist, hype: DEFAULT_HYPE }` (replacing `{ artist, home: null }`)
- [x] 3.6 Remove `clearHypes()` call from `clearAll()`; remove `import { clearHypes }` from storage import

## 4. FollowServiceClient — Correct Guest listFollowed

- [x] 4.1 Update `listFollowed()` guest branch in `src/services/follow-service-client.ts` to return `guest.follows` directly (remove `hype: 'watch' as const` hardcode)

## 5. Data Merge — Read Hype from Follow Entries

- [x] 5.1 Find the signup merge path that calls `guest.getHypes()` and update it to iterate `guest.follows`, calling `SetHype` for entries where `hype !== DEFAULT_HYPE`

## 6. ConcertService — Reference DEFAULT_HYPE

- [x] 6.1 Replace `entry?.hype ?? 'watch'` literal in `src/services/concert-service.ts` with `entry?.hype ?? DEFAULT_HYPE`

## 7. Artist Filter Bar — Remove Header Chips

- [x] 7.1 Remove `<ul class="chips-list">` block (the active filter chips) from `src/components/artist-filter-bar/artist-filter-bar.html`
- [x] 7.2 Remove chip-related CSS rules (`.chips-list`, `.chip`, `.chip-name`, `.chip-dismiss`) from `src/components/artist-filter-bar/artist-filter-bar.css`
- [x] 7.3 Remove `dismiss(id)` method from `src/components/artist-filter-bar/artist-filter-bar.ts` if it is only used by the chip dismiss button

## 8. Signup Banner — Update Copy

- [x] 8.1 Update `myArtists.signupBanner.message` in `src/locales/ja/translation.json` to `"フォロー情報を保存してコンサート通知を受け取ろう！"`
- [x] 8.2 Update `myArtists.signupBanner.message` in `src/locales/en/translation.json` to `"Save your followed artists and get concert notifications."`

## 9. Verification

- [x] 9.1 Run `make check` and confirm all lint + unit tests pass
- [ ] 9.2 Manually verify: follow 2+ artists as guest → set hype on one → navigate to dashboard → confirm laser beam renders for the hype-elevated artist
- [ ] 9.3 Manually verify: activate artist filter → confirm no chips appear in header; filter icon shows active state
- [ ] 9.4 Manually verify: signup banner shows updated copy in both Japanese and English locales
