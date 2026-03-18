## Why

Artist logos (clearLOGO from fanart.tv) displayed on event cards have poor visibility when the card background color clashes with the logo's dominant color. The current background hue is derived from a hash of the artist name, which has no relationship to the logo's actual colors. This leads to dark logos on dark backgrounds (e.g., SPYAIR) and same-hue logos on same-hue backgrounds (e.g., Suchmos red logo on reddish background).

## What Changes

- The fanart sync pipeline (CronJob + event consumer) will analyze each artist's best logo image to extract dominant color properties (hue, lightness, chromaticity).
- Analysis results will be stored alongside existing fanart data in the `fanart` JSONB column.
- The proto `Fanart` message will be extended with a `LogoColorProfile` message containing the extracted color metadata.
- The frontend will use `LogoColorProfile` to compute an optimal card background color that maximizes logo visibility while preserving color variety across the app.

## Capabilities

### New Capabilities
- `logo-color-analysis`: Automatic extraction of logo dominant color properties and optimal background color derivation for artist event cards.

### Modified Capabilities
- `artist-image`: The Fanart entity, proto message, and sync pipeline gain a `LogoColorProfile` sub-entity populated during image sync.

## Impact

- **specification**: `Fanart` proto message extended with `LogoColorProfile` sub-message.
- **backend**: Fanart entity gains `LogoColorProfile` field. Sync job and event consumer updated to download logo PNG and run color extraction. Mapper updated to include analysis in proto response.
- **frontend**: `color-generator.ts` and `artist-color` custom attribute updated to prefer `LogoColorProfile` data over name-hash hue. CSS custom properties may include `--artist-bg-lightness`.
- **dependencies**: No new external dependencies. Go `image/png` + `image/color` standard library suffice for pixel analysis. OKLCH conversion uses fixed matrix math (no library needed).
