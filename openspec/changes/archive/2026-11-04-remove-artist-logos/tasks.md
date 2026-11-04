## 1. Proto (specification)

- [x] 1.1 In `proto/liverty_music/entity/v1/artist.proto`, remove `Fanart.hd_music_logo`, `music_logo` and `logo_color_profile` and the `LogoColorProfile` message, and reserve the numbers 3, 4, 6 and the three names (design "Reserve the removed proto fields"); verify `buf lint` and `buf format -d` pass and `scripts/check-forbidden-words.py` passes
- [x] 1.2 Open the proto PR with the `buf skip breaking` label, merge it, publish the GitHub Release and confirm the `buf-release.yml` run succeeds

## 2. Entity and operations (backend: components/entity/artist, fetch-image, analyze-logo, resolve-images)

- [x] 2.1 Upgrade the generated schema package to the release of 1.2; remove `Fanart.HDMusicLogo`, `MusicLogo`, `LogoColorProfile`, the `LogoColorProfile` type, the `LogoImageFetcher` interface, `AnalyzeLogo` and their tests and mocks, and stop the fanarttv client decoding the logo kinds and drop its `LogoFetcher`; verify `make check` passes with no reference to them left (`git grep -n -i -E "logo(color|imagefetcher|fetcher)|hdmusiclogo|musiclogo|analyzelogo"` finds nothing outside migrations)
- [x] 2.2 Annotate the fanarttv client contract tests with `@spec components/entity/artist/resolve-images` for "All kinds available", "Some kinds available" (with artist_thumb and artist_background) and "No entry", adding a test where none verifies the scenario; verify they pass

## 3. Usecase and adapter (backend: components/usecase/artist/sync-artist-image)

- [x] 3.1 Make `ArtistImageSyncUseCase` take the image resolver and the repository only, and stop the event consumer and the daily image sync job building the logo fetcher; verify one unit test per scenario of "SyncArtistImage records the artist's images" passes with the operations mocked, annotated `@spec components/usecase/artist/sync-artist-image` "Images found", "No images", "Empty MBID"
- [x] 3.2 Stop `adapter/pb` mapping the logo and the color profile, and switch the logo test data of the repository and story tests to `artist_background` or `artist_thumb`; verify the `adapter/pb` artist tests pass and `make check` passes
- [x] 3.3 Annotate the discover-artists story test with `@spec stories/discover-artists` "Newly discovered artist" and "Already registered artist", adding the assertions where the test does not yet check the scenario; verify it passes
- [x] 3.4 Open the backend PR (OpenSpec Traceability filled), merge, release; after the rollout, confirm read-only that the event consumer and the next daily image sync job log no error

## 4. Frontend (components/infrastructure/fan/web/global/live-highway)

- [x] 4.1 Upgrade the generated schema package to the release of 1.2; remove `hdMusicLogo`, `musicLogo`, `logoColorProfile`, `LogoColorProfile`, `bestLogoUrl`, `artistHueFromColorProfile` and `logoColorProfileFrom` with their exports, and the event card's `logoUrl`, `logoError`, `onLogoError`, `eventChanged` reset and `.artist-logo` rules; verify `make check` passes with no reference to them left
- [x] 4.2 Update the artist mapper, artist model, guest storage and concert store tests and the E2E `artist-image-ui` fixtures to carry only background and portrait URLs; verify the tests annotated with "ListFollowed returns artist with fanart", "ListFollowed returns artist without fanart" and "Dashboard events enriched with fanart" pass, and that `e2e/functional/artist-image-ui.spec.ts` passes against a local build with the detail sheet still showing the background image
- [x] 4.3 Open the frontend PR (OpenSpec Traceability filled), merge, release; confirm the fan web rollout runs the new version

## 5. Archive

- [x] 5.1 Remove the hd_music_logo and music_logo kinds and the fanart.logo_color_profile row from the Purpose of `components/entity/artist` and the logo from its opening sentence, and drop "profiling the best logo's colors along the way" from the Purpose of `components/usecase/artist/sync-artist-image`; verify `openspec validate --specs` passes
- [x] 5.2 Delete the emptied `components/entity/artist/fetch-image` and `analyze-logo` specs; verify `openspec validate --specs` and `python3 scripts/check-spec-layout.py` pass
