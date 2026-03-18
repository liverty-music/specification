## Why

Unmatched event cards apply aggressive dimming filters (`brightness(0.35) grayscale(0.8)`) to artist logos, making them nearly invisible against the dark card backgrounds. The matched vs. unmatched distinction is already clear from the neon glow, spotlight, and box-shadow effects on matched cards — the additional dimming is redundant and harms artist recognition. Additionally, logos are left-aligned within cards instead of centered, text fallback is too small, and logo images are constrained to a tiny fixed height (`3rem`).

## What Changes

- Remove `brightness(0.35) grayscale(0.8)` filter from unmatched card logos
- Remove `opacity: 0.6` from unmatched card text fallback
- Center-align artist logos and text within event cards
- Increase text fallback font size for artists without logos — currently too similar to location label size
- Scale logo images to fill card space using cqi units instead of fixed `3rem` height

## Capabilities

### New Capabilities

- `card-logo-presentation`: Visual presentation rules for artist logos and text within event cards (alignment, visibility, sizing)

### Modified Capabilities

_None_

## Impact

- `frontend/src/components/live-highway/event-card.css` — remove unmatched dimming rules, add centering, adjust sizing
