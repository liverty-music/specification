## Why

Discovery page bubbles load artist images from fanart.tv via `bestLogoUrl()`, causing mass image loading errors in the browser console. The `artist-image-ui` change (2026-03-17) explicitly marked "DNA Orb / discovery bubble images" as a Non-Goal, but the image loading code was never removed. Additionally, when images fail to load (`img.complete=true`, `naturalWidth=0`), the artist name text position shifts downward due to an inconsistent condition check, causing off-center layout.

## What Changes

- Remove all image loading, caching, and rendering from `DnaOrbCanvas` bubble rendering
- Redefine bubble content as artist name only, centered within the bubble
- Add adaptive font sizing and line wrapping for artist names based on bubble radius and name length

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `artist-discovery-dna-orb-ui`: Add explicit "Bubble Content Display" requirement defining that bubbles show artist name only (no images), with adaptive font sizing and line wrapping

## Impact

- `frontend/src/components/dna-orb/dna-orb-canvas.ts`: Remove `preloadImages`, `imageCache`, image rendering in `renderBubble`, `bestLogoUrl` import. Rewrite text rendering with adaptive sizing and wrapping.
- `frontend/src/components/dna-orb/absorption-animator.ts`: Remove `logoUrl` parameter from `startAbsorption` if it references image data.
- No backend or proto changes required.
