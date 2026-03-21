## Why

Chromatic artist logos (e.g., YOASOBI's pink logo) blend into the card background because both the logo and background use the same `--artist-hue`. The current "adaptive contrast" background (clamped to 12–30% lightness, 0.03 chroma) was intended to create matched/unmatched visual hierarchy, but this dimming strategy has been retired. With unmatched cards now using vivid artist colors, same-hue logos become invisible against their own color family.

Additionally, logo images used as artist names do not stretch to fill the card width, leaving excess whitespace.

## What Changes

- **Background hue derivation**: For chromatic logos, shift the card background hue to the complementary angle (`dominantHue + 180° mod 360`) so the logo color always contrasts with the background. Achromatic logos continue to use the name-hash fallback.
- **Remove unmatched dimming**: Replace the clamped dark background with the standard `--artist-color` for unmatched cards.
- **Logo width fill**: Stretch artist logo images to fill the card's inline size while maintaining aspect ratio.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `logo-color-analysis`: The frontend background color derivation requirement changes — chromatic logos use the complementary hue (dominantHue + 180°) instead of the logo's own hue for the card background.
- `card-logo-presentation`: Logo sizing requirement changes — logos stretch to fill card width (`inline-size: 100%`) instead of being constrained to `max-inline-size: 80%`.

## Impact

- **Frontend CSS** (`event-card.css`): Unmatched background rule simplified; logo sizing updated.
- **Frontend TS** (`adapter/view/artist-color.ts`): `artistHueFromColorProfile` returns complementary hue for chromatic logos.
- **No backend changes**: Complementary hue is a pure display concern computed in the frontend.
- **No proto changes**: Existing `LogoColorProfile` fields are sufficient.
