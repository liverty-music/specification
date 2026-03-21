## Context

Event cards on the dashboard use `--artist-hue` (derived from `LogoColorProfile.dominantHue` or a name-hash fallback) for both the card background and logo glow effects. For chromatic logos like YOASOBI (pink, hue ≈ 335°), the logo and background share the same hue family, causing the logo to blend into the background.

The previous "adaptive contrast" strategy (clamping background lightness to 12–30% with minimal chroma) has been retired. Cards now use vivid artist colors, making hue collision more visible.

Current data flow:
1. Backend `AnalyzeLogo()` extracts `dominantHue`, `dominantLightness`, `isChromatic`
2. Frontend `artistHueFromColorProfile()` returns `dominantHue` directly (or name-hash fallback)
3. CSS uses `--artist-hue` for background: `oklch(65% 0.2 var(--artist-hue))`
4. Logo renders on top in its original color → same hue = invisible

## Goals / Non-Goals

**Goals:**
- Ensure artist logos are always visually distinct from the card background
- Remove the retired unmatched dimming logic from CSS
- Make logos fill the card width for better visual impact

**Non-Goals:**
- Changing the backend `AnalyzeLogo` logic or proto schema
- Modifying matched card spotlight effects (those already use different rendering)
- WCAG contrast ratio guarantees (logos are decorative images, not functional text)

## Decisions

### Decision 1: Complementary hue via frontend calculation

**Choice**: Compute `(dominantHue + 180) % 360` in `artistHueFromColorProfile()`.

**Alternatives considered**:
- *Backend `BackgroundHue` field*: Would require proto schema change, BSR release, and cross-repo coordination for a pure display concern. Rejected — disproportionate cost.
- *Triadic shift (+120°)*: Less contrast than complementary. Some hue pairs (e.g., red → green vs red → cyan) offer better separation at 180°.
- *Desaturated background (chroma → 0)*: Would lose the per-artist color identity on the dashboard.

**Rationale**: 180° shift maximizes perceptual distance on the hue wheel. The computation is trivial (one addition + modulo) and belongs entirely in the view layer.

### Decision 2: Remove unmatched dimming, use `--artist-color-dim` directly

**Choice**: Replace the `.event-card:not([data-matched])` background rule with `background-color: var(--artist-color-dim)` (oklch 65% 0.03 hue). This uses the already-defined CSS custom property, keeping the background muted enough that matched cards with full `--artist-color` and spotlight effects remain visually distinct.

**Rationale**: `--artist-color-dim` (low chroma 0.03) is a soft tinted background that avoids the "dark grey" look while reserving vivid saturation for matched cards. Since the hue is now the complementary angle, even this low-chroma background won't collide with the logo.

### Decision 3: Logo `inline-size: 100%`

**Choice**: Set `.artist-logo { inline-size: 100%; max-inline-size: none; }` with `object-fit: contain` preserved.

**Rationale**: Logos are transparent PNGs (clearLOGO format, 800×310 or 400×155). `contain` ensures aspect ratio is preserved while the logo stretches to fill the card width. The existing `max-block-size: 25cqi` remains as a vertical constraint.

## Risks / Trade-offs

- **Some complementary pairs may feel unexpected** (e.g., yellow logo → purple background) → Acceptable because the dashboard already shows diverse colors per artist; the complementary pair reinforces visual distinctiveness.
- **Achromatic logos are unchanged** → Name-hash hue is random, which is fine — achromatic logos (white/black text) contrast with any hue at the current lightness/chroma levels.
- **Logo stretching on very wide cards** → Mitigated by `object-fit: contain` (maintains aspect ratio) and `max-block-size: 25cqi` (vertical cap). Only the horizontal space increases.
