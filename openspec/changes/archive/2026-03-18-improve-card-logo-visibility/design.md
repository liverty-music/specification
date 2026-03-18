## Context

Event cards display artist logos (fanart.tv ClearLOGO PNGs) or text fallback names. Currently, unmatched cards dim logos with `brightness(0.35) grayscale(0.8)` and text with `opacity: 0.6`. Matched cards already have strong visual differentiation via neon glow borders, spotlight gradients, and box-shadow effects, making the dimming redundant and harmful to readability. Logos are left-aligned by default, constrained to `max-block-size: 3rem`, and text fallback is too small.

Card height is content-based (no fixed grid row height). Each lane (`li.lane`) is a `container-type: inline-size` context, making `cqi` units available for proportional sizing.

## Goals / Non-Goals

**Goals:**
- Ensure artist logos and text are legible on unmatched cards
- Center-align logos and text within all event cards
- Scale logos and text proportionally to lane width
- Maintain clear visual distinction between matched and unmatched cards

**Non-Goals:**
- Changing matched card effects (spotlight, glow, etc.)
- Modifying the background lightness calculation (`--artist-bg-lightness` logic)

## Decisions

### 1. Remove unmatched dimming entirely (not just reduce it)

Remove both the logo `filter` and text `opacity` rules rather than tweaking values. The matched/unmatched distinction relies on additive effects (glow, spotlight, border) on matched cards — not subtractive dimming on unmatched cards.

**Alternative considered:** Reduce `brightness` from 0.35 to 0.6 — rejected because any dimming reduces logo legibility against the already-dark backgrounds, and the visual distinction doesn't need it.

### 2. Center logos via `align-items: center` on the flex parent

Add `align-items: center` to `.event-card`. This centers both logos and text fallback horizontally. The `location-label` below also centers, which is consistent with the card's compact layout.

**Alternative considered:** `margin-inline: auto` on `.artist-logo` only — rejected because it wouldn't center the text fallback, requiring a separate rule.

### 3. Increase text fallback font size using cqi units

Change from `clamp(12px, 5cqi, 24px)` to `clamp(14px, 8cqi, 32px)`. The `cqi` unit is relative to the lane container's inline-size, so text scales proportionally across lane widths.

### 4. Scale logo images using cqi units

Replace fixed `max-block-size: 3rem` with `25cqi` (container-query inline unit). The card height is content-based (not fixed by grid rows), so the logo size directly determines the card height. Using `cqi` ensures logos scale proportionally with the lane width, consistent with the text fallback approach.

**Alternative considered:** `flex: 1` to fill card space — rejected because card height is content-based (not fixed by grid rows), so `flex: 1` would expand the card infinitely rather than constraining the logo to a proportional size.

## Risks / Trade-offs

- **[Visual hierarchy weakened]** → Mitigated by the strong matched card effects (glow, spotlight, animated border). The delta between "normal card" and "glowing neon card" is already very high.
- **[Centered logos may look odd for very wide logos]** → Mitigated by existing `max-inline-size: 80%` constraint. ClearLOGO images are typically horizontally oriented and look natural when centered.
