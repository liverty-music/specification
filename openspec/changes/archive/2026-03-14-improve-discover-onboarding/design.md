## Context

The discover page uses a CSS grid with 4 rows (`auto auto auto 1fr`) for search bar, genre chips, onboarding HUD, and bubble area. The HUD persists throughout onboarding with countdown messages, occupying vertical space and reducing the bubble canvas. Additionally, the search bar's SVG icon lacks explicit sizing, causing layout overflow on mobile.

The existing `OrbRenderer` already supports `injectColor(hue)` and `swirlIntensity` for per-follow visual effects, and `AbsorptionAnimator` handles the bubble-to-orb flight path. However, `swirlIntensity` decays to 0 in ~1 second, providing no sense of accumulation across follows.

The discover page currently serves both onboarding and normal users with the same layout; the HUD is conditionally shown via `show.bind`. This change keeps that shared-route approach but replaces the HUD with a one-time popover.

## Goals / Non-Goals

**Goals:**
- Make each follow feel rewarding through persistent orb visual evolution
- Maximize bubble area by removing the HUD from the grid
- Use native Popover API with CSS-only animations (no JS animation hacks)
- Fix search bar layout issues (icon sizing)
- Keep the existing spotlight/coach-mark system for dashboard transition intact

**Non-Goals:**
- Sound effects or haptic feedback (future enhancement)
- Changes to the absorption animation path or dissolve particles
- Backend API changes
- Modifications to the coach-mark or spotlight system
- Persisting `baseIntensity` across page navigations

## Decisions

### 1. Popover API with `popover="auto"` for light-dismiss

**Choice**: Native `popover="auto"` attribute with CSS `@starting-style` for entry animation.

**Why**: `popover="auto"` provides light-dismiss (tap outside to close) for free, renders in the top layer (no z-index management), and supports CSS-only open/close transitions via `:popover-open` + `@starting-style` + `transition-behavior: allow-discrete`.

**Alternatives considered**:
- `<dialog>` element: Blocks interaction, requires explicit close action. Too heavy for a quick onboarding hint.
- JS class toggling with `display: none`: Legacy pattern. Requires JS for animation timing and doesn't get top-layer benefits.

**Animation approach**:
```css
.onboarding-guide {
  opacity: 0;
  translate: 0 1rem;
  transition:
    opacity 400ms ease,
    translate 400ms ease,
    display 400ms ease allow-discrete,
    overlay 400ms ease allow-discrete;

  &:popover-open {
    opacity: 1;
    translate: 0 0;
  }

  @starting-style {
    &:popover-open {
      opacity: 0;
      translate: 0 1rem;
    }
  }
}
```

Only `opacity` and `translate` are transitioned — both compositor-thread properties.

### 2. Easing-curve `baseIntensity` accumulation in OrbRenderer

**Choice**: Add a `baseIntensity` field to `OrbRenderer` that accumulates per follow using a diminishing-returns curve: `baseIntensity = 1 - 1 / (1 + followCount * 0.5)`.

**Why**: Linear accumulation (+0.2 per follow) makes later follows feel less impactful because the visual delta is constant. The easing curve front-loads impact: follow #1 gives +0.33, follow #2 gives +0.17 on top, follow #5 gives +0.06. This matches the user's desire for "the first follow should have maximum wow factor."

**Curve values**:
| Follow # | baseIntensity | Delta |
|----------|---------------|-------|
| 0 | 0.00 | — |
| 1 | 0.33 | +0.33 |
| 2 | 0.50 | +0.17 |
| 3 | 0.60 | +0.10 |
| 5 | 0.71 | +0.05 |
| 10 | 0.83 | +0.02 |

**Integration point**: `baseIntensity` is added to the existing `intensity` (bindable `orbIntensity`) when computing effective glow, particle count, and swirl speed. The `update()` method uses `effectiveSwirl = baseIntensity + swirlIntensity` for particle speed multiplier.

### 3. Use bubble's existing hue for color injection

**Choice**: Pass the bubble's pre-computed hue (from `artistHue(name)` in `dna-orb-canvas.ts`) directly through the absorption pipeline to `injectColor`.

**Why**: The color pipeline already flows `renderBubble(hue) → handleInteraction(hue) → AbsorptionAnimator(hue) → OrbRenderer.injectColor(hue)`. No new hue computation is needed. The user sees the bubble's color enter the orb, creating a direct visual connection.

### 4. Increase particle injection count per follow

**Choice**: Change `injectColor` from replacing 5-8 particles to 10-15 particles per follow.

**Why**: With 60 total particles, 5-8 replacements (8-13%) produce a subtle visual shift. 10-15 replacements (17-25%) create a noticeable color burst that makes each follow feel impactful. Combined with the `swirlIntensity` spike, this creates a dramatic "color stream entering the orb" effect.

### 5. Grid simplification to 3 rows

**Choice**: Change `grid-template-rows` from `auto auto auto 1fr` to `auto auto 1fr`, removing the HUD row.

**Why**: The popover renders in the top layer, outside the grid flow. The third `auto` row was only for the HUD. Removing it gives the bubble area (`1fr`) maximum vertical space.

### 6. Fix search icon sizing at the block level

**Choice**: Add explicit `inline-size` and `block-size` to `.search-icon` and `.clear-button` in the block CSS, plus `flex-shrink: 0` to prevent flex compression.

**Why**: Per CUBE CSS methodology, intrinsic sizing is a block responsibility. SVG elements without explicit dimensions expand to fill their flex container. The fix belongs in the block layer, not composition.

## Risks / Trade-offs

**[Popover API browser support]** → `popover` is Baseline 2024. All target browsers support it. No polyfill needed.

**[`@starting-style` browser support]** → Baseline 2024 (Chrome 117+, Safari 17.5+, Firefox 129+). Our minimum targets are met. Fallback: popover appears instantly without animation, which is acceptable.

**[`baseIntensity` resets on page navigation]** → By design. The orb restarts from zero when the user leaves and returns. This is acceptable because: (a) returning users see their followed artists with checkmarks, providing context, and (b) the orb quickly re-intensifies if they follow more artists.

**[Removed progress feedback]** → Users no longer see "あと2組！" countdown. Mitigation: the orb's visual evolution provides implicit progress, and the spotlight coach-mark appears when 3+ artists with concerts are found, clearly signaling "next step available."

**[Performance with 10-15 particle replacements]** → Marginal. `injectColor` is O(n) over 60 particles, called once per follow (not per frame). The existing performance monitoring/quality scaling handles any frame drops.
