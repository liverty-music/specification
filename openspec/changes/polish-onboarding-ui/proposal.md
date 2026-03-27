## Why

The onboarding flow has several UI polish issues identified during review:
1. The DNA orb at the bottom of the Discovery page grows too large (MAX_RADIUS=120), crowding the bubble area
2. The dashboard lane intro skips the coach mark and opens the Home Selector immediately, breaking the guided flow defined in the final design
3. The My Artists header shows an artist count badge `(6)` that is not in the specification
4. The signup-prompt-banner uses a horizontal layout (text + button side-by-side) that is cramped on mobile — text wraps to 3 lines and the CTA button is visually buried

## What Changes

- **DNA Orb sizing**: Reduce `MAX_RADIUS` from 120 to 90, adjust `GROWTH_PER_FOLLOW` to 7.5 and `LINEAR_STEPS` to 4 so the orb reaches max at 4 follows. Shrink `orbZoneHeight` proportionally to reclaim bubble area.
- **Lane Intro order**: Show HOME stage coach mark first, then open Home Selector after user acknowledges — matching the spec flow.
- **My Artists header**: Remove the `(N)` artist count from the page header.
- **Signup prompt banner**: Change from horizontal (flex-row) to vertical (flex-column) layout — text full-width on top, CTA button full-width below.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `artist-discovery-dna-orb-ui`: Orb max size and growth curve constants change
- `dashboard-lane-introduction`: Home phase must show coach mark before opening Home Selector
- `my-artists`: Remove artist count from header
- `signup-prompt-banner`: Layout changes from horizontal to vertical

## Impact

- **Frontend only** — all changes are in `frontend/src/`
- Files affected:
  - `components/dna-orb/stage-effects.ts` (orb sizing constants)
  - `components/dna-orb/bubble-physics.ts` (orbZoneHeight)
  - `routes/dashboard/dashboard-route.ts` (lane intro sequencing)
  - `routes/my-artists/my-artists-route.html` (header template)
  - `components/signup-prompt-banner/signup-prompt-banner.css` (layout)
- No API, backend, or infrastructure changes
