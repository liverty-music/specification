## 1. Match Logic (TypeScript)

- [x] 1.1 Add `isHypeMatched(hype: HypeLevel, lane: LaneType): boolean` pure function to `dashboard-service.ts` using ordinal comparison (HYPE_ORDER[hype] >= LANE_ORDER[lane])
- [x] 1.2 Add `matched: boolean` field to `LiveEvent` interface in `live-event.ts`
- [x] 1.3 Pass lane parameter to `concertToLiveEvent()` and compute `matched` using `isHypeMatched`
- [x] 1.4 Update `convert` lambda in `protoGroupToDateGroup` to pass lane ('home' | 'nearby' | 'away') to `concertToLiveEvent`

## 2. Template Binding (HTML)

- [x] 2.1 Add `data-matched.bind="event.matched"` to the `<article>` element in `event-card.html`
- [x] 2.2 Add conditional clearLOGO / text rendering: `<img if.bind="event.clearLogoUrl" class="artist-logo">` with `<span else class="artist-name">` fallback

## 3. Card Styling — Matched (CSS)

- [x] 3.1 Remove per-tier selectors (`[data-hype="watch"]`, `[data-hype="home"]`, `[data-hype="nearby"]`, `[data-hype="away"]`) and their keyframes from `event-card.css`
- [x] 3.2 Remove `@property --hype-border-angle` registration
- [x] 3.3 Register `@property --hue-drift` (syntax: `<number>`, initial: 0, inherits: false)
- [x] 3.4 Add `[data-matched]` base styles: radial-gradient spotlight background (chroma 0.20), 2px border at 40%, dual glow (outer 16px 50% + inset 12px 15%), `overflow: hidden`
- [x] 3.5 Add `[data-matched] .artist-logo` styles: multi-layer `filter: drop-shadow()` neon contour glow using artist-color
- [x] 3.6 Add `[data-matched] .artist-name` styles: multi-layer `text-shadow` neon glow using artist-color
- [x] 3.7 Add spotlight sweep `::before` pseudo-element on `[data-matched]`: radial-gradient, `mix-blend-mode: screen`, `animation: spotlight-sweep 6s ease-in-out infinite`
- [x] 3.8 Add `@keyframes spotlight-sweep` (translateX -60% → 60%)
- [x] 3.9 Add color drift animation on `[data-matched]`: `animation: color-drift 8s ease-in-out infinite`, `--artist-color` references `calc(var(--artist-hue) + var(--hue-drift))`
- [x] 3.10 Add `@keyframes color-drift` (--hue-drift: 0 → 30 → -30 → 0)

## 4. Card Styling — Unmatched (CSS)

- [x] 4.1 Add `:not([data-matched])` base styles: flat desaturated background (chroma 0.03), 1px white/5% border, no glow, no animations
- [x] 4.2 Add `:not([data-matched]) .artist-logo` styles: `filter: brightness(0.35) grayscale(0.8)`
- [x] 4.3 Add `:not([data-matched]) .artist-name` styles: no text-shadow, reduced opacity
- [x] 4.4 Add SVG noise texture `::after` pseudo-element on `:not([data-matched])` at 8% opacity

## 5. Accessibility (CSS)

- [x] 5.1 Add `@media (prefers-reduced-motion: reduce)` to disable spotlight-sweep and color-drift animations; static glow/border/saturation remain
- [x] 5.2 Verify `alt` attribute is bound to `event.artistName` on clearLOGO `<img>`

## 6. Verification

- [x] 6.1 Unit test `isHypeMatched` — all 12 combinations (4 hype × 3 lane) return correct boolean
- [x] 6.2 Visual check: matched cards show spotlight sweep, neon glow, and color drift
- [x] 6.3 Visual check: unmatched cards show desaturation, noise texture, dimmed logo
- [x] 6.4 Visual check: text fallback cards (no clearLogoUrl) show text-shadow neon instead of drop-shadow
- [x] 6.5 Visual check: `prefers-reduced-motion: reduce` disables animations, static effects remain
- [x] 6.6 Run `make check` in frontend repo (lint + test)
