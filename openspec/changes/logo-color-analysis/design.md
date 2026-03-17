## Context

Event cards display artist logos (clearLOGO PNGs from fanart.tv) on colored backgrounds. The background hue is currently derived from a deterministic hash of the artist name (`color-generator.ts`), which has no relationship to the logo's actual colors. This causes visibility issues where logo and background colors are too similar.

The fanart sync pipeline (CronJob + NATS event consumer) already downloads fanart metadata. This change extends it to also download the best logo image, analyze its pixels, and store color metadata alongside the existing fanart JSONB.

## Goals / Non-Goals

**Goals:**
- Ensure artist logos are always visually distinguishable from their card background
- Preserve color variety across the app (avoid monotone dark/light backgrounds)
- Keep the analysis pipeline within the existing sync infrastructure (no new services)

**Non-Goals:**
- Real-time / client-side color extraction (ruled out due to CORS and performance)
- Storing the logo image itself (only metadata; images are served directly from fanart.tv CDN)
- Changing the matched/unmatched card visual system (spotlight effects remain hue-driven)

## Decisions

### Decision 1: Store hue + lightness metadata, not a computed background color

**Choice:** Store `dominantHue`, `dominantLightness`, and `isChromatic` as analysis output. The frontend derives the final background color from these values.

**Why not store a complete background color?**
The current CSS architecture derives 6+ color variants from a single `--artist-hue` custom property (spotlight glow, dim background, border, shadow). Storing a finished `oklch(...)` string would break this derivation chain and force frontend redesign. Storing raw analysis data preserves CSS flexibility and allows design iteration without re-running the sync pipeline.

### Decision 2: Three-class logo classification

Logos are classified into three types based on pixel analysis:

| Type | Condition | Background Strategy |
|------|-----------|-------------------|
| `CHROMATIC` | >30% of non-transparent pixels have OKLCH chroma > 0.04 | Use logo's dominant hue (same hue, low chroma background) so the logo color pops |
| `ACHROMATIC_LIGHT` | Predominantly achromatic, mean lightness > 0.6 | Use name-hash hue freely (any hue works against white logos), keep background dark |
| `ACHROMATIC_DARK` | Predominantly achromatic, mean lightness ≤ 0.6 | Use name-hash hue freely, raise background lightness so dark logo is visible |

**Why not just complementary hue (hue+180)?** Complementary colors maximize hue distance but can produce garish combinations (red logo on cyan). For chromatic logos, the logo's own hue with a desaturated background is more aesthetically pleasing — the logo becomes the color accent.

**Why keep name-hash for achromatic logos?** White and black logos have no color information. Using the name-hash preserves the existing color variety. Only lightness needs adjustment.

### Decision 3: Color extraction in Go using standard library

**Algorithm:**
1. Download the best logo image (PNG) via HTTP
2. Decode with `image/png`
3. Iterate all pixels, skip fully transparent (alpha < 10)
4. Convert each pixel sRGB → Linear RGB → OKLab → OKLCH using fixed-coefficient matrix math
5. Classify pixel as chromatic (chroma > 0.04) or achromatic
6. For chromatic pixels, build a hue histogram (36 bins of 10° each)
7. Output: peak hue from histogram, mean lightness, chromatic ratio

**Why OKLCH over HSL?** OKLCH is perceptually uniform — equal numeric differences correspond to equal perceived differences. HSL has well-known issues where "50% lightness" varies wildly by hue. Since the goal is perceptual contrast, OKLCH is the right space. The frontend already uses OKLCH in CSS (`oklch()` function).

**Why no external library?** The sRGB→OKLab conversion is a 3x3 matrix multiply + cube root. ~30 lines of Go. Adding a dependency for this is not justified.

### Decision 4: Store analysis inside existing `fanart` JSONB

**Choice:** Add a `logoColorProfile` key to the existing `fanart` JSONB column rather than a separate column.

```json
{
  "artistthumb": [...],
  "hdmusiclogo": [...],
  "logoColorProfile": {
    "dominantHue": 210,
    "dominantLightness": 0.15,
    "isChromatic": true
  }
}
```

**Why?** The analysis is derived from and tightly coupled to the logo data. It should be refreshed whenever fanart data is refreshed. Keeping it in the same JSONB ensures atomicity and avoids schema migration for a new column.

### Decision 5: Proto extension — `LogoColorProfile` message inside `Fanart`

```protobuf
message Fanart {
  // ... existing fields ...
  optional LogoColorProfile logo_color_profile = 6;
}

message LogoColorProfile {
  float dominant_hue = 1;        // 0-360, OKLCH hue angle
  float dominant_lightness = 2;  // 0-1, OKLCH lightness
  bool is_chromatic = 3;         // true if logo has significant color
}
```

**Why inside Fanart?** LogoColorProfile is meaningless without fanart data — it's derived from the logo image. Placing it as a peer field on `Artist` would create a confusing ownership model.

### Decision 6: Frontend fallback chain

```
if (artist.fanart?.logoColorProfile) {
  // Use analysis-driven hue + lightness
  if (logoColorProfile.isChromatic) {
    hue = logoColorProfile.dominantHue  // logo's own hue family
  } else {
    hue = hash(artistName)          // preserve variety
  }
  bgLightness = derived from logoColorProfile.dominantLightness
} else if (artist.fanart) {
  // Has fanart but no analysis (transition period)
  hue = hash(artistName)
} else {
  // No fanart at all
  hue = hash(artistName)
}
```

Fully backward-compatible. The `artist-color` custom attribute gains an optional `logoColorProfile` input. When absent, behavior is identical to current.

### Decision 7: Analyzed image must be the same image returned in proto

**Choice:** The color analysis target is always the same image that the proto mapper selects via `BestByLikes` — HDMusicLogo first, falling back to MusicLogo. The analysis and the proto response must never reference different images.

**Why?** If a different image were analyzed, the derived background color would not match the logo the user actually sees. The selection logic (`BestByLikes` with HDMusicLogo → MusicLogo fallback) is shared between the mapper and the analysis pipeline.

### Decision 8: Decouple fanart API call from image analysis

**Choice:** The color analysis function (`AnalyzeLogo`) is a pure function in the entity layer that accepts an `image.Image` and returns a `*LogoColorProfile`. It has no knowledge of HTTP, fanart.tv, or any I/O. The usecase layer orchestrates: select best logo URL → HTTP download → PNG decode → call `AnalyzeLogo`.

**Why?** This separation ensures:
- `AnalyzeLogo` is testable with synthetic images (no HTTP mocking needed)
- The usecase layer can be tested by injecting a mock HTTP client that returns fixed PNG bytes
- The analysis algorithm can evolve independently from the sync pipeline

## Risks / Trade-offs

**[Risk] Logo image download adds latency to sync pipeline** → The sync job already throttles API calls. Logo download is one additional HTTP request per artist. Given the daily cadence and circuit breaker, this is acceptable. The consumer path (ARTIST.created) adds ~200ms for the image download.

**[Risk] Some logos may have misleading dominant colors** (e.g., a red logo with a tiny blue accent that skews the histogram) → The 36-bin histogram with >30% chromatic threshold is conservative. Edge cases can be tuned by adjusting the threshold.

**[Risk] OKLCH chroma threshold (0.04) may misclassify near-gray colors** → This is a tuning parameter. Start conservative and adjust based on visual results.

**[Trade-off] Analysis is only as fresh as the sync cycle** → If fanart.tv updates a logo, the analysis won't update until the next sync (daily or 7-day refresh). This is acceptable since logo changes are rare.
