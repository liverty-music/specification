## Why

Dashboard event cards currently style based on hype level alone (e.g., "away" artist always gets maximum glow). But hype expresses *how far a user would travel* for an artist — the real signal is whether the concert's venue proximity falls within the artist's hype radius. An "away" artist on every stage should light up; a "home" artist on the away stage should not. Without this match logic, all cards in a lane look roughly the same, defeating the purpose of hype as a prioritization tool.

Additionally, a separate change is introducing fanart.tv clearLOGO images (transparent PNGs of artist wordmarks). When available, these replace the text artist name on cards. The visual effects must work with both transparent PNG logos and text fallbacks, leveraging `filter: drop-shadow()` for logos (contour-following neon glow) and `text-shadow` for text.

## What Changes

- **Replace per-hype-level card styling with hype-lane match styling**: Cards are visually "lit" when the concert's lane falls within the artist's hype radius, and "dim" when it does not.
- **Move match logic to TypeScript**: The hype >= lane comparison is business logic. A pure function in the service layer computes `matched: boolean` and exposes it as a `data-matched` attribute. CSS only knows matched vs. not-matched.
- **Festival-grade matched effects**: Matched cards use a spotlight sweep animation, color drift (hue oscillation), neon contour glow on clearLOGO (or text-shadow fallback), elevated saturation, and dual-layer glow — evoking a live festival stage.
- **Faded poster unmatched treatment**: Unmatched cards use desaturation, noise texture overlay, and dimmed logos — evoking faded ink on an old concert poster.
- **clearLOGO / text dual rendering**: Event cards conditionally render `<img>` (clearLOGO PNG) or `<span>` (text fallback). Visual intent is identical; implementation differs (`filter: drop-shadow` vs. `text-shadow`).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `passion-level`: Replace "Hype Visual Indicators on Dashboard Cards" requirement. Card styling is determined by hype-lane match, not hype tier alone. Add festival-stage animations (spotlight sweep, color drift) and clearLOGO/text dual rendering with appropriate glow effects.
- `typography-focused-dashboard`: Replace "Must Go Mutation UI" requirement with the hype-lane match model.

## Impact

- **Frontend only** — no proto, backend, or infrastructure changes.
- `frontend/src/services/dashboard-service.ts`: Add match computation when building `LiveEvent`.
- `frontend/src/components/live-highway/live-event.ts`: Add `matched: boolean` field to `LiveEvent` interface.
- `frontend/src/components/live-highway/event-card.html`: Bind `data-matched` attribute; conditional `<img>` / `<span>` rendering for clearLOGO.
- `frontend/src/components/live-highway/event-card.css`: Replace 4-tier hype selectors with matched/unmatched selectors, add spotlight sweep and color drift animations, add clearLOGO-specific `filter` rules.
- **Dependency**: Assumes `clearLogoUrl` field will be available on `LiveEvent` via the separate fanart.tv change. This change defines how that field is visually consumed, not how it is fetched.
