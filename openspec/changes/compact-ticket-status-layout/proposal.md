## Why

On the concert detail sheet, the "チケット状況" (ticket status) control occupies far more vertical space than its information density warrants — roughly two-thirds of it is the "結果" (outcome) phase, which stacks the win route (`当選・未入金 → ↓ → 入金済み`) vertically inside one bordered card and the lose route (`落選`) inside a second bordered card below it. On a mobile sheet this pushes the primary action buttons (公式情報を見る, etc.) far down the scroll. The control should fit in roughly half its current height. Separately, the flow arrow (`›`) between nodes is visually cramped — it has no dedicated inline margin and a hairline glyph, so it reads as squeezed between the chips.

## What Changes

- Lay the outcome phase out **horizontally** in a single row — the win route (`当選・未入金 › 入金済み`) and the lose route (`落選`) sit side by side, separated by a lightweight divider, instead of two vertically stacked bordered cards.
- Remove the per-route bordered card chrome (border + padding); rely on the divider and existing route dimming to keep the win/lose routes distinguishable.
- Replace the vertical down-arrow (`↓`) connector with the horizontal `›` connector, unifying both phases on one connector style.
- Give the flow arrow dedicated inline breathing room (explicit `margin-inline`) and a slightly larger glyph so it no longer reads as cramped — applies to both the process row and the new outcome row.
- Net effect: the ticket-status control's vertical footprint drops to ~half of its current height while preserving every node, the radiogroup semantics, and the canonical per-status label/icon/hue.

Non-goals: no change to journey state machine, status values, i18n keys, the canonical status presentation map, or any RPC behavior. Tap targets stay at the 44px accessibility minimum.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `concert-detail`: The journey-status control's outcome phase changes from a vertically stacked two-card layout to a compact single-row horizontal layout, halving the control's vertical footprint while keeping all status nodes and radiogroup behavior.

## Impact

- **frontend** only: `src/components/live-highway/event-detail-sheet.css` (outcome/route/arrow rules), and a small template touch in `event-detail-sheet.html` to retire the `journey-arrow-down` modifier.
- DOM structure, radiogroup roles, `data-testid` hooks, and keyboard navigation handler are preserved; existing component/E2E tests for the journey control should continue to pass (with possible visual-baseline regeneration).
- No specification/proto, backend, or BSR impact.
