## 1. LongPress Custom Attribute

- [x] 1.1 Create `src/custom-attributes/long-press.ts` with `@customAttribute('long-press')`, `@bindable` callback, 500ms timer, pointer event listeners, and 10px movement-cancel threshold
- [x] 1.2 Guard listener attachment with `matchMedia('(pointer: coarse)').matches` so desktop skips the attribute
- [x] 1.3 Register `LongPressCustomAttribute` in `src/main.ts`

## 2. ArtistUnfollowSheet Component

- [x] 2.1 Create `src/components/artist-unfollow-sheet/artist-unfollow-sheet.ts` with `@bindable artist`, `@bindable open`, and unfollow-confirmed event dispatch
- [x] 2.2 Create `src/components/artist-unfollow-sheet/artist-unfollow-sheet.html` using `<bottom-sheet>` primitive with artist name, danger "Unfollow" button, and cancel button
- [x] 2.3 Create `src/components/artist-unfollow-sheet/artist-unfollow-sheet.css` with danger button styles
- [x] 2.4 Register `ArtistUnfollowSheet` in `src/main.ts`

## 3. My Artists Route Integration

- [x] 3.1 Add `selectedArtistForUnfollow: MyArtist | null` and `unfollowSheetOpen: boolean` properties to `MyArtistsRoute`
- [x] 3.2 Add `openUnfollowSheet(artist: MyArtist)` method that sets the selected artist and opens the sheet
- [x] 3.3 Add `onUnfollowConfirmed()` method that calls the existing `unfollowArtist()` and closes the sheet
- [x] 3.4 Add `long-press` attribute to `<tr>` in `my-artists-route.html` with callback bound to `openUnfollowSheet(artist)`
- [x] 3.5 Add `<artist-unfollow-sheet>` element to `my-artists-route.html` outside `<tbody>`, bound to `selectedArtistForUnfollow` and `unfollowSheetOpen`

## 4. Translations

- [x] 4.1 Add `myArtists.unfollowSheet.confirm`, `myArtists.unfollowSheet.cancel`, `myArtists.unfollowSheet.sheetLabel` keys to `src/locales/ja/translation.json`
- [x] 4.2 Add the same keys to `src/locales/en/translation.json`
- [x] 4.3 Add `pageHelp.myArtists.longPressTip` key (long-press gesture explanation) to both locale files

## 5. Help Page Content

- [x] 5.1 Update help page content for `my-artists` to include the long-press-to-unfollow gesture description

## 6. Verification

- [x] 6.1 Run `make lint` in `frontend/` — zero errors
- [x] 6.2 Run `make test` in `frontend/` — all tests pass
- [x] 6.3 Manual smoke test on touch emulation: long-press opens sheet, confirm unfollows, cancel dismisses
- [x] 6.4 Manual smoke test on desktop: trash icon still visible and functional, no long-press behaviour
