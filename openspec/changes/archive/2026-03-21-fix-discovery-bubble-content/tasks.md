## 1. Remove image infrastructure from DnaOrbCanvas

- [x] 1.1 Remove `imageCache` field, `preloadImages()` method, and `bestLogoUrl` import from `dna-orb-canvas.ts`
- [x] 1.2 Remove all `preloadImages()` calls in `attached()`, `artistsChanged()`, `reloadBubbles()`, `spawnBubblesAt()`
- [x] 1.3 Remove `this.imageCache.clear()` from `detaching()` and `reloadBubbles()`
- [x] 1.4 Remove image drawing block in `renderBubble()` (lines 470-478: the `img?.complete && img.naturalWidth > 0` block)

## 2. Remove image references from absorption animator

- [x] 2.1 Remove `imageUrl` field from `AbsorptionAnimation` interface in `absorption-animator.ts`
- [x] 2.2 Remove `imageUrl` parameter from `startAbsorption()` method signature
- [x] 2.3 Update all `startAbsorption()` call sites in `dna-orb-canvas.ts` (in `handleInteraction` and `spawnAndAbsorb`) to remove the `logoUrl` argument

## 3. Implement adaptive text rendering in renderBubble

- [x] 3.1 Fix text vertical position: always use `y` (bubble center) instead of conditional `img?.complete ? y + r * 0.5 : y`
- [x] 3.2 Implement word-wrap function: split artist name into words, greedily fit per line using `ctx.measureText()`, return array of lines
- [x] 3.3 Implement adaptive font sizing: base size from `radius * 0.38`, reduce if widest line exceeds usable diameter (`radius * 1.6`)
- [x] 3.4 Render multi-line text: draw each line offset from vertical center by `lineHeight * (lineIndex - (totalLines - 1) / 2)`

## 4. Verify

- [x] 4.1 Run `make check` in frontend to ensure lint and tests pass
