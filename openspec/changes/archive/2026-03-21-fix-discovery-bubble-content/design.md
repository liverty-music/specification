## Context

The `DnaOrbCanvas` component contains image loading code (`preloadImages`, `imageCache`, `renderBubble` image drawing) that predates the `artist-image-ui` change which explicitly marked bubble images as a Non-Goal. This dead code causes two user-visible bugs:

1. **Console errors**: fanart.tv URLs loaded via `new Image()` with `crossOrigin='anonymous'` fail (404, CORS, broken links), producing mass `ERR_FAILED` / network errors in the console.
2. **Off-center text**: When image load fails, `img.complete` is `true` but `naturalWidth` is 0. The text position condition (`img?.complete ? y + r * 0.5 : y`) shifts the name downward even though no image renders (the draw condition checks `img?.complete && img.naturalWidth > 0`).

Current bubble rendering: gradient background + attempted image + single-line text + outline.
Target bubble rendering: gradient background + adaptive multi-line centered text + outline.

## Goals / Non-Goals

**Goals:**
- Remove all image loading/caching/rendering from bubble and absorption code
- Display artist name only, centered horizontally and vertically in each bubble
- Scale font size inversely with name length relative to bubble radius
- Wrap long names across multiple lines to avoid overflow

**Non-Goals:**
- Changing bubble gradient colors, outline, or physics behavior
- Modifying the `bestLogoUrl` helper itself (other components use it)
- Adding text truncation with ellipsis (prefer wrapping)
- Changing absorption animation visuals beyond removing the unused `imageUrl` parameter

## Decisions

### 1. Remove image infrastructure entirely from DnaOrbCanvas

Delete `imageCache`, `preloadImages()`, all `bestLogoUrl` calls in `dna-orb-canvas.ts`, and the image drawing block in `renderBubble()`. Remove the `imageUrl` field from `AbsorptionAnimation` interface and `startAbsorption()` parameter.

**Why**: This code is dead by spec (Non-Goal in artist-image-ui). Removing it eliminates both bugs at the source rather than patching around them.

### 2. Adaptive font sizing based on bubble radius and character count

Use a simple formula: `baseFontSize = radius * 0.38`, then scale down proportionally if the text width exceeds the available diameter. Canvas `measureText()` provides the width measurement.

**Why**: Bubbles have varying radii (30-45px). A fixed font size doesn't work. Scaling from the radius ensures proportionality, and `measureText()` is already available in the 2D context with no performance cost.

### 3. Word-wrap via manual line splitting

Split the artist name into words. Greedily fit words per line using `measureText()`. If a single word exceeds the bubble width, reduce font size further. Render each line offset from center by `lineHeight * (lineIndex - (totalLines - 1) / 2)`.

**Why**: Canvas 2D has no built-in word wrap. Manual splitting with greedy fit is simple, deterministic, and handles the common cases (1-3 word names, occasional long single words like "BABYMETAL" or "Aerosmith").

### 4. Text vertical centering always at bubble center

Always position text at `y` (bubble center). Remove the conditional `y + r * 0.5` offset entirely since there's no image to make room for.

**Why**: Directly fixes the off-center bug. With no image, the text should always be vertically centered.

## Risks / Trade-offs

**[Very long artist names]** — Names exceeding ~30 characters at minimum font size may still be hard to read at small bubble radii (30px). Acceptable because this is a rare edge case and the bubble tap still works as a discovery mechanism even if the name is small.

**[CJK character wrapping]** — Word-based splitting doesn't work for CJK names without spaces (e.g., Japanese artist names). For now, character-level overflow reduction handles this acceptably. Can be revisited if CJK artist discovery becomes a priority.
