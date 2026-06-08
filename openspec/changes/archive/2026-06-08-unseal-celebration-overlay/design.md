## Context

The celebration overlay (`celebration-overlay.css`) currently darkens the whole viewport behind its text:

```css
.celebration-overlay {
  background: oklch(0% 0 0deg / 80%);   /* full-screen 80% black veil */
  backdrop-filter: blur(8px);            /* + heavy blur of everything behind */
}
```

During exploration this was verified against a maximally vibrant timetable (oklch 75% chroma 0.3 cards): the veil collapses the festival palette to ~20%-luminance muddy blocks. The "封印" (seal) is this full-screen veil.

Note on a separate, already-resolved issue: an earlier screenshot showed the heading and sub-text split to the top/bottom thirds with an empty center. Reproducing the **current** CSS (HEAD `6521462`, which added `align-content: center`) showed the two lines centered with only the 16px row-gap between them. That layout problem is already fixed and is **out of scope** here; this change is purely about the backdrop.

Constraints:
- CUBE CSS methodology, `@layer block` + `@scope (celebration-overlay)`, design tokens from `tokens.css`.
- Behavior (two-tier gating, once-per-tier, confetti flag, tap-to-dismiss, reduced-motion) must not change.
- Legibility must hold over the brightest stage cards (near-stage cyan `oklch(82% 0.16 195)`, accent green, amber) — the worst case for white text.

## Goals / Non-Goals

**Goals:**
- Reveal the completed timetable as the visual payoff: keep the screen edges fully colorful behind the overlay.
- Guarantee heading + sub-text contrast on any background, including the brightest cards.
- Keep the change CSS-only and minimal (low regression risk).

**Non-Goals:**
- No change to celebration tiers, gating, dismissal, confetti, or reduced-motion logic.
- No change to the centering/spacing of the text (already fixed).
- No new animation system, no JS changes (a possible spotlight-sweep is deferred).

## Decisions

### Decision: Adopt the "text-lens" backdrop (explored option C1)

Replace the full-screen opaque veil with a light overall scrim plus a **feathered radial darkening sized to the text group**, layered with the existing brand-purple glow halo:

```css
.celebration-overlay {
  background: oklch(0% 0 0deg / 18%);   /* light overall scrim — edges stay vivid */
}
.celebration-overlay::before {          /* dark "lens" hugging the text, + purple halo */
  background:
    radial-gradient(ellipse 78% 24% at 50% 47%,
      oklch(0% 0 0deg / 72%) 0%, oklch(0% 0 0deg / 40%) 52%, transparent 80%),
    radial-gradient(ellipse 64% 32% at 50% 47%,
      oklch(72% 0.26 294deg / 26%) 0%, transparent 72%);
}
```

Heading/sub-text shadows are strengthened; the sub-text additionally gets a thin dark outline (multi-stop `text-shadow`) as a hard legibility floor.

**Why C1 over the alternatives** (all mocked over identical vibrant + worst-case bright backgrounds during exploration):

| Option | Idea | Verdict |
|---|---|---|
| A | Thin veil + vignette | Great balance, but dims the whole screen more than needed |
| B | Top-down spotlight cone | Best world-fit (matches event-card spotlight / highway lasers) but heavier; deferred as a follow-up |
| C0 | Light scrim + purple halo only | Sub-text fails on bright near-stage cards (legibility hole) |
| **C1** | **Light scrim + text-lens + halo** | **Edges fully vibrant AND text legible on the worst-case background — chosen** |
| C2 | Near-zero scrim + text outline only | Most see-through, but small sub-text is marginal on bright cards |
| D | Translucent text panel | Safe legibility, but re-introduces a "box" and kills immersion |

C1 keeps the "most see-through / most vibrant" character the product wanted while closing C0's legibility hole by darkening **only** behind the text rather than the whole viewport.

### Decision: Drop the full-screen `backdrop-filter: blur(8px)`

The full-screen blur is the second half of the seal and adds GPU cost. The text-lens provides contrast locally, so the global blur is removed. (An optional very light blur could live inside the lens region only; default is none.)

## Risks / Trade-offs

- [Lower overall scrim could hurt heading contrast on a pathological all-white card cluster] → the text-lens + strengthened shadows + sub-text outline provide a contrast floor independent of the background; validated against the brightest stage palette during exploration.
- [Intentional UI change invalidates frontend visual baselines] → regenerate baselines per the project's baseline-refresh process as part of the PR.
- [Removing the global blur changes the "frosted" feel some may expect] → acceptable and intended; the goal is to reveal, not frost.

## Migration Plan

CSS-only, no data or API migration. Ship via the normal frontend PR → `make check` → visual-baseline regeneration → merge → release flow. Rollback is reverting the single CSS file.

## Open Questions

- Should the brand-purple halo hue track the matched-artist hue for extra "personalization", or stay fixed brand purple? Default: fixed brand purple (simplest, on-brand).
- Defer or include the option-B spotlight sweep as a later enhancement? Default: defer.
