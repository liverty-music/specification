## Context

Dashboard event cards currently apply visual effects (border, glow, animation) based on the artist's hype level alone. The CSS uses `[data-hype="away"]`, `[data-hype="nearby"]`, etc. to escalate visual intensity. However, the meaningful signal for users is whether a concert falls within their declared hype radius for that artist — i.e., whether `hype >= lane`.

The existing code already has both `data-hype` (artist's hype level) and `data-lane` (concert proximity) on each card element. The `LiveEvent` interface carries `hypeLevel`, and the lane is determined by the `DateGroup` structure (`home`, `nearby`, `away` arrays).

A separate change is introducing fanart.tv clearLOGO images — transparent PNGs of artist wordmarks. When available, these replace the text artist name. This changes the effect strategy: transparent PNGs enable `filter: drop-shadow()` which follows the exact logo contour, producing a neon-sign effect impossible with rectangular `text-shadow`.

## Goals / Non-Goals

**Goals:**
- Cards that a user "should attend" (hype radius covers the venue proximity) are visually prominent with festival-stage energy
- Cards outside the hype radius are visually muted like a faded concert poster
- Match logic lives in TypeScript as a testable pure function
- CSS knows only `matched` vs `not-matched` — no business rules in stylesheets
- ClearLOGO and text fallback produce the same visual intent through different CSS mechanisms

**Non-Goals:**
- Changing card size or font size based on match (poor mobile UX on narrow lanes)
- Modifying the hype level system itself (tiers, persistence, RPC)
- Fetching or caching clearLOGO images (separate change)
- Backend changes

## Decisions

### Decision 1: Binary `matched` attribute instead of per-tier CSS selectors

**Choice**: Replace the 4-tier CSS escalation (`[data-hype="watch"]` through `[data-hype="away"]`) with a single `[data-matched]` boolean attribute.

**Rationale**: The per-tier approach encoded business logic (hype hierarchy) in CSS. The binary approach keeps CSS purely presentational. The match truth table:

| hype \ lane | home | nearby | away |
|-------------|------|--------|------|
| watch       | -    | -      | -    |
| home        | LIT  | -      | -    |
| nearby      | LIT  | LIT    | -    |
| away        | LIT  | LIT    | LIT  |

**Alternative considered**: CSS compound selectors (`[data-hype="away"][data-lane="home"]`). Rejected because it leaks the hype inclusion hierarchy into CSS — any change to the hype model requires CSS updates.

### Decision 2: Match computation in `dashboard-service.ts`

**Choice**: Compute `matched` in `concertToLiveEvent()` where lane context is available, rather than in the component.

**Rationale**: `concertToLiveEvent` already receives `hypeLevel` and is called within the `convert` function that knows which lane array it's processing. Adding lane as a parameter and computing the match there keeps the logic co-located with event construction.

**Alternative considered**: Compute in `EventCard` component using `lane` and `event.hypeLevel` bindables. Rejected because the component shouldn't contain business logic — it's a presentational component.

### Decision 3: Pure function `isHypeMatched(hype, lane)`

**Choice**: Extract match logic into a standalone pure function.

**Rationale**: Testable in isolation. The function encodes a simple ordinal comparison:

```
HYPE_ORDER = { watch: 0, home: 1, nearby: 2, away: 3 }
LANE_ORDER = { home: 1, nearby: 2, away: 3 }
matched = HYPE_ORDER[hype] >= LANE_ORDER[lane]
```

`watch` (0) is never >= any lane (minimum 1), so watch artists never match.

### Decision 4: Festival-stage visual treatment for matched cards

**Matched** cards evoke a live festival stage with three layered effects:

1. **Spotlight beam cone** (`::before` + `::after` pseudo-elements): A vertical light beam cone illuminates the card from above via `linear-gradient` shaped by `mask-image: radial-gradient(ellipse)`. A bright contact flash (`::after`) pulses at the card's top edge where the beam hits, using layered `box-shadow` for glow. GPU-composited, no repaint.

2. **Color drift** (`@property --hue-drift`): The artist-color hue oscillates ±30° over 8 seconds. Because `--artist-color` is referenced by background, border, glow, and drop-shadow, a single `@property` animation drives all color elements simultaneously.

3. **Neon contour glow**: For clearLOGO (transparent PNG), multi-layer `filter: drop-shadow()` produces a glow that follows the exact logo contour — a neon sign effect. For text fallback, equivalent `text-shadow` layers produce a similar impression. Both use the drifting `--artist-color`.

**Static properties** (always present, survive `prefers-reduced-motion`):
- Background: radial-gradient spotlight (static center position)
- Chroma: 0.20 (elevated saturation)
- Border: 2px solid artist-color at 40% opacity
- Outer glow: `box-shadow: 0 0 16px` at 50% opacity
- Inner glow: `inset 0 0 12px` at 15% opacity

**Alternative considered**: Wristband pulse (breathing box-shadow animation). Rejected because `box-shadow` animation triggers repaint per frame, and spotlight sweep + color drift already provide sufficient motion.

### Decision 5: Faded poster treatment for unmatched cards

**Unmatched** cards evoke a faded, aged concert poster:
- Chroma: 0.03 (near monochrome)
- Background: flat desaturated artist-color
- Border: 1px solid `white/5%`
- No glow
- ClearLOGO: `filter: brightness(0.35) grayscale(0.8)` (dimmed and desaturated)
- Text fallback: no text-shadow, reduced opacity
- SVG noise texture overlay at 8% opacity via `::after` pseudo-element
- No animations

### Decision 6: ClearLOGO / text conditional rendering

**Choice**: Use Aurelia `if.bind` / `else` to conditionally render `<img class="artist-logo">` or `<span class="artist-name">` based on `event.clearLogoUrl` presence.

**Rationale**: The two elements need fundamentally different CSS properties (`filter: drop-shadow` vs. `text-shadow`). Separate elements with distinct class names allow clean CSS targeting without complex compound selectors.

The `data-matched` attribute on the parent card element controls matched/unmatched styling. The logo/text elements inherit their glow treatment from the card's match state.

## Risks / Trade-offs

- **[Spotlight sweep performance on many cards]** → The `::before` pseudo-element uses only `transform` and `mix-blend-mode: screen`, staying on the compositor thread. `overflow: hidden` on the card clips the spotlight. Acceptable even with 10+ visible matched cards.
- **[Color drift browser support]** → `@property` is supported in Chrome 85+, Safari 15.4+, Firefox 128+. Fallback: if `@property` is unsupported, `--hue-drift` stays at 0 and the card displays a static (non-drifting) artist-color. All other effects still work.
- **[Watch artists always dim]** → Watch-level artists never match any lane, so their cards are always muted. This is intentional — "watch" means "just checking", not "planning to go".
- **[ClearLOGO availability]** → Not all artists will have clearLOGO images. The text fallback must feel equally polished. The neon `text-shadow` at matched intensity ensures text-only cards are not second-class.
- **[SVG noise texture performance]** → Inline SVG noise as a pseudo-element overlay on every unmatched card. Mitigation: Use a shared CSS `background-image` (cached once), keep opacity low, apply `will-change: auto` (not `transform`) to avoid layer promotion.
