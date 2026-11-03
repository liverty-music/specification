## Why

Artists carry two logo images and a color profile of the best logo, but no screen shows them: the event card writes the artist name as text and takes its color from a hash of the name. Still, every image sync downloads each artist's logo, measures its colors and stores the result, and the API sends all of it to the app. Removing the feature drops that work and the dead code on every side.

## What Changes

- **BREAKING** The `Fanart` message loses `hd_music_logo`, `music_logo` and `logo_color_profile`, and the `LogoColorProfile` message is removed; their field numbers and names are reserved. The PR carries the `buf skip breaking` label. An app that still reads them sees them absent, which it already handles.
- An artist's images no longer include logos, and an artist has no logo color profile. The square portrait (artist_thumb), the wide backdrop (artist_background, the hero of the event detail sheet) and the wide banner (music_banner) stay.
- The image sync records the images it looks up and no longer downloads or analyzes a logo.
- The operations that only served the logo are retired: `Artist.FetchImage` (download a logo) and `Artist.AnalyzeLogo` (measure its colors).
- No migration: logo keys already stored with an artist's images are ignored when read and dropped at the artist's next sync. Artists nobody follows are not synced again and keep them unread.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/entity/artist`: removes "The best logo prefers high definition" and "Logo color profile values are in range". (Purpose) The fanart attribute loses the hd_music_logo and music_logo kinds, the fanart.logo_color_profile row goes, and the opening sentence stops mentioning a logo.
- `components/entity/artist/fetch-image`: every requirement removed; the capability is retired.
- `components/entity/artist/analyze-logo`: every requirement removed; the capability is retired.
- `components/entity/artist/resolve-images`: the example of a partial result names image kinds that remain.
- `components/usecase/artist/sync-artist-image`: records the images without a logo profile; "A logo failure does not stop the sync" is removed. It still relies on Artist.ResolveImages (modified above: it no longer returns logo kinds), Artist.UpdateFanart and Artist.ListStaleOrMissingFanart, whose requirements are unchanged. (Purpose) "profiling the best logo's colors along the way" goes.
- `components/infrastructure/fan/web/global/live-highway`: the app maps only the background and portrait URLs from an artist's images.
- `stories/discover-artists`: a newly discovered artist ends up with its images and canonical name, no logo color profile.

## Impact

- **specification**: `proto/liverty_music/entity/v1/artist.proto` (fields 3, 4, 6 of `Fanart` and `LogoColorProfile` removed and reserved), released before the downstream work.
- **backend**: the logo kinds and color profile of the stored images, the logo download and color analysis, their use in the image sync (event consumer and daily job), the API mapping, and their tests and mocks.
- **frontend**: the logo fields of the artist mapping and model, the best-logo and logo-hue helpers, the event card's unused logo state and style, and their tests.
- **cloud-provisioning**: none. The image catalog key is still needed for the other images.
