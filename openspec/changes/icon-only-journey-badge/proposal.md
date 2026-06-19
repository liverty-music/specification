## Why

The concert-card journey badge renders the status icon plus a full text label (e.g. `👀 追跡中`) as a pill anchored to the card's top-right corner. On the dashboard timetable the cards are small — especially in the NEAR/AWAY lanes — so the ~75px wide pill overlaps the artist name and breaks the card layout. The label text is redundant on a dense, glanceable surface: the icon alone communicates status, and the full label is still available in the concert-detail status control where there is room for it.

## What Changes

- The concert-card journey badge SHALL render the status **emoji only** — no text label, and no background pill or hue.
- The badge SHALL sit on the card's **top-right corner, bleeding half outside the card** (notification-badge convention), so it never collides with the bottom-aligned artist name regardless of name length or lane. This requires removing the redundant `overflow: hidden` from the card (clipping is already handled by `border-radius` / mask).
- The dashboard filter chips and the concert-detail status control are unchanged — they keep showing icon, label, **and** hue.
- This relaxes the cross-cutting "every rendering shows icon and text label" and "icon and hue are the same across all surfaces" rules so the compact card badge may show the emoji alone, while the canonical map remains the single source of truth.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `journey-status-presentation`: The "Meaning survives without colour" requirement currently mandates that **every** journey-status rendering present icon **and** text label. The compact concert-card badge will now show the icon only. The requirement is reframed so each surface chooses an appropriate density (icon-only for the card badge, icon+label for chips and the detail control) while every surface still relies on a non-colour cue and the canonical map.

## Impact

- Frontend only; no proto, backend, or RPC changes.
- `frontend/src/components/live-highway/event-card.html` — badge markup (icon only, `aria-label` for the accessible name).
- `frontend/src/components/live-highway/event-card.css` — badge corner-bleed at top-right (`translate`), `overflow: hidden` removed from the card, bare emoji (no background/pill/hue), per-status `--_journey-text` and `--_journey-bg` vars removed.
- Visual regression baselines for the dashboard/timetable will need regeneration.
