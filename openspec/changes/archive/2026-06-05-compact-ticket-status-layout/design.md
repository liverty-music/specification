## Context

The ticket-status control in `event-detail-sheet` renders the ticket journey as a radiogroup of status nodes across two phases: a process phase (`追跡中 › 申込済み`, already horizontal) and an outcome phase. The outcome phase is the height bottleneck: it stacks the win route (`当選・未入金 → ↓ → 入金済み`) vertically inside one bordered card and the lose route (`落選`) inside a second bordered card below. Measured on a mobile sheet, the outcome phase alone is ~214px of a ~330px control — roughly two-thirds.

Each node carries `min-block-size: 2.75rem` (44px) as a tap target, so the win route alone is two 44px nodes + a down-arrow + a route label + card padding ≈ 146px. The structure is pure CSS/template geometry; the journey state machine, status values, i18n keys, and the canonical per-status label/icon/hue map (`journey-status-presentation`) are untouched.

The flow arrow (`.journey-arrow`) has no dedicated margin — its only breathing room is the container's `gap: var(--space-3xs)` (~4–5px) — and uses a hairline `›` at `--step--1`, so it reads as cramped between the chips.

## Goals / Non-Goals

**Goals:**
- Cut the ticket-status control's vertical footprint to ~half (~330px → ~165px) on mobile.
- Keep every status node, the radiogroup semantics, keyboard navigation, `data-testid` hooks, and the canonical label/icon/hue.
- Give the flow arrow visible breathing room and a non-hairline glyph in both phases.

**Non-Goals:**
- No change to the journey state machine, status enum, i18n keys, or the canonical presentation map.
- No reduction of the 44px tap-target minimum.
- No backend/proto/BSR impact.

## Decisions

### D1: Lay the outcome phase out horizontally (single row), not vertically stacked cards

The win route and lose route move into one horizontal row: `[当選・未入金] › [入金済み]  ·  [落選]`. This collapses the dominant ~146px vertical win-route into a single 44px row.

- **Why over alternatives:**
  - *Per-card horizontal (keep both bordered cards, only flatten the win route internally)* — keeps the card framing but only reaches ~25% reduction; misses the "half" target.
  - *Shrink node height / tighten gaps only* — 44px is the accessibility tap-target floor; shrinking trades misclicks for height and still falls short of half.
  - *Single unified 5-node horizontal timeline* — elegant but will not fit 5 nodes on a 360px viewport.
- The horizontal single-row approach is the only option that hits the ~half target with a local CSS change.

### D2: Remove per-route bordered card chrome; distinguish routes with a divider + existing dimming

The `border` + `padding` on `.journey-route` is dropped. Win vs lose separation is carried by a lightweight inline divider (e.g. a centered middot/separator) plus the existing `data-dimmed` route dimming and per-status hue. This removes double framing and reclaims vertical padding.

### D3: Unify connectors on the horizontal `›`; retire `journey-arrow-down`

With the outcome row horizontal, the `↓` connector (`.journey-arrow-down`) is no longer meaningful. Both phases use the same `›` connector. The `journey-arrow-down` modifier class is removed from the template and CSS.

### D4: Give the flow arrow dedicated inline margin and a larger glyph

`.journey-arrow` gets explicit `margin-inline` (≈`--space-2xs`) so its spacing no longer depends on the container `gap`, and the glyph size rises to ~`--step-0` so it is not hairline. Applies uniformly to both the process row and the new outcome row.

### D5: Mobile narrow-width fallback — allow wrap

At 360px the outcome row holds three nodes plus connector/divider. The row is allowed to `flex-wrap`; if it wraps, `落選` drops to a second line. Even the wrapped worst case (~2×44px ≈ 110px) stays well under the current ~214px, so the half-height target holds either way.

## Risks / Trade-offs

- **Weaker win/lose visual separation** (cards removed) → Mitigation: keep the divider, route dimming, and distinct per-status hues; the lose route stays visually distinct via its red hue and the separator.
- **Radiogroup arrow-key expectations shift** (outcome was vertical, now horizontal) → Mitigation: the existing `onJourneyKeydown` handler already drives selection across the node set; verify Left/Right and Up/Down both still traverse the nodes and adjust the handler only if a direction regresses.
- **Visual regression baselines** → Mitigation: this is an intentional UI change; expect to regenerate the frontend visual baselines (delete the visual-baselines CI artifact to force regen) and re-confirm component/E2E `journey-btn` tests pass.
- **Cramped row on very narrow / large-font devices** → Mitigation: D5 wrap fallback prevents overflow; nodes keep `flex: 1 1 auto`.

## Migration Plan

Pure frontend, no data or API migration. Ship as a normal frontend PR. Rollback is reverting the CSS/template diff. No feature flag needed.

## Open Questions

- Exact divider treatment between the win and lose routes (middot `·`, a thin vertical rule, or just spacing) — to be finalized during implementation against the live sheet.
