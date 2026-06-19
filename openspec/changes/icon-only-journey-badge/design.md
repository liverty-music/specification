## Context

The concert card (`event-card`) renders a journey-status badge as an absolutely-positioned pill in the top-right corner, showing the status icon followed by the translated label (`👀 追跡中`, `💰 当選・未入金`, …). The badge derives its icon, label, and hue from the canonical `JOURNEY_STATUS_CONFIG_MAP` (the `journey-status-presentation` capability).

On the dashboard timetable the cards are intentionally small and dense — three lanes (HOME / NEAR / AWAY) of fan-followed concerts. The label-bearing pill is ~75px wide and sits at the top, where the artist name also begins (the card's flex column has no `min-block-size`, so `justify-content: end` collapses and content starts at the top). The result is the badge overlapping the artist name. The label is redundant here: on a glanceable surface the icon alone conveys the status, and the full label remains in the concert-detail status control where space allows.

Note: `tracking` is **not** equivalent to following an artist. Following an artist is what surfaces a concert on the dashboard at all; `tracking` is a user-initiated, per-concert journey state ("I'm watching this specific event for ticket sales"). Every journey status — including `tracking` — is meaningful information worth showing on the card.

## Goals / Non-Goals

**Goals:**
- Remove the badge/artist-name overlap on the timetable cards.
- Keep all five journey statuses visible on the card via their canonical icon.
- Preserve the canonical map as the single source of icon/label/hue.
- Keep an accessible name for the badge (screen readers still announce the status).

**Non-Goals:**
- No change to the dashboard filter chips or the concert-detail status control (they keep icon + label).
- No change to which statuses appear, the state machine, or any backend/proto/RPC surface.
- No redesign of the card layout itself beyond the badge.

## Decisions

**Decision: Card badge shows icon only.**
The icon is the directness the user asked for — emoji are recognised at a glance and carry the semantic weight. The label is dropped from the card to reclaim horizontal space. Rationale: on a dense card the label is redundant given the icon; the label still lives on the detail control. Alternative considered — keeping the label but shrinking the font: rejected, the pill still consumes width and overlaps.

**Decision: Place the badge on the top-right corner, bleeding half outside the card.**
`position: absolute` at the top-right corner plus `translate: 40% -40%` so the chip sits ON the corner, roughly half outside the card. Rationale: any in-card position can collide with the bottom-aligned artist name, because in the HOME lane there is no venue label and the centred name can fill the whole card (verified empirically — a bottom-right in-card badge overlapped the name on 4 of 5 cards). Bleeding past the corner separates the badge from the content region entirely, so it cannot collide regardless of name length. Top-right is the universal notification-badge position (zero learning), is scanned early (top + corner), and breaks the card silhouette for pre-attentive pop-out. Alternatives considered: (a) bottom-right in-card — re-creates the overlap for full-card names in the HOME lane; (b) a wrapper element (`overflow:visible` outer + `overflow:hidden` inner surface) — rejected as unnecessary DOM, and `event-card__surface` BEM naming would not match this component's plain class convention (`.artist-name`, `.journey-badge`); (c) `overflow: clip` + `overflow-clip-margin` to bleed from a single element — rejected, `overflow-clip-margin` is not Baseline (Firefox-only as of 2026, unsupported in Chrome/Edge/Safari).

**Decision: Remove `overflow: hidden` from `.event-card` (no wrapper).**
For the badge to bleed past the corner it must not be clipped by the card. The card's `overflow: hidden` turns out to be redundant: the gradient background is clipped by `border-radius`, the noise `::after` self-rounds via `border-radius: inherit`, and the matched-card beam `::before` is hidden at the corners by its own radial mask. Removing it lets the badge bleed with zero new DOM and zero new classes, and was verified to leave the card's rounded corners, gradient, noise, and matched glow/beam visually intact. The outer `.concert-scroll { overflow-inline: hidden }` still bounds the timetable horizontally; the small bleed at the outermost lanes (HOME-left / AWAY-right) is absorbed by the `.lane` padding (verified: badges on the rightmost AWAY lane are not clipped).

**Decision: Bare emoji, no background pill or hue.**
With no text and corner placement, the badge is just the status emoji — no background fill, no border, no per-status hue. The emoji is the sole, self-coloured cue. Rationale: the corner-bleed placement already makes the emoji read as a badge, and a coloured pill behind it added visual weight without extra meaning on a dense surface. Consequently both the per-status `--_journey-text` (label tint) and `--_journey-bg` (pill hue) custom properties are removed, along with the now-dead `padding`/`border-radius`/flex-centering on the chip. Trade-off accepted below: dropping the hue removes the colour half of the colour+shape double-encoding; the emoji shape (👀📝💔💰🎟️) remains a non-colour cue, so the status is still distinguishable without relying on colour.

## Risks / Trade-offs

- [Icon-only loses the explicit text label on the card] → The accessible name is preserved via `aria-label` (translated label), and the full label remains on the detail control and filter chips. The icon set is already designed to be meaning-bearing per the existing "Meaning survives without colour" intent.
- [Visual regression baselines will fail] → Regenerate the dashboard/timetable visual baselines as part of shipping (known frontend flow: delete the visual-baselines artifact to force regen).
- [Corner-bleed still overlaps the first line for a pathologically long name that fills the entire card] → Only the extreme top-right corner of line 1 is touched (a ~1px corner), and only for unrealistically long single-artist names (~60 chars). Acceptable; far better than the in-card positions which sit on the name body.
- [Removing `overflow: hidden` could expose a future overflowing child] → Today every child is bounded (logo `max-block-size`, text `overflow-wrap: break-word`) and clipping is handled by `border-radius`/`mask`. If a future child needs hard clipping, scope it to that child rather than re-adding card-level `overflow: hidden`, which would clip the badge.
