## Context

The Ticket Status control lives in `EventDetailSheet` (`src/components/live-highway/`). It lets an authenticated user self-report their ticket-acquisition status for a concert. The five statuses are stored as a single `TicketJourneyStatus` value per `(user, event)`; the backend enforces **no** state machine (any status is settable at any time — see `ticket-journey` spec). The UI is therefore a self-report selector, not a guided wizard.

Current implementation renders the five statuses via `repeat.for` as a flat horizontal wrap of pills. The active state is shown with a 25%-opacity tinted background plus a per-status outline color defined as scoped `--_journey-*` custom properties. This produces two problems documented in the proposal: (1) the selected pill is barely visible against the dark sheet, and (2) the flat row hides the real branching journey.

The real journey is a branching DAG, not a linear list:

```
TRACKING ─▸ APPLIED ─┬─▸ LOST                 (failure, terminal)
                     └─▸ UNPAID ─▸ PAID        (success route)
```

`UNPAID` and `PAID` both imply "won the lottery"; "当選" is a derived grouping label, not a stored status.

## Goals / Non-Goals

**Goals:**
- Make the currently-selected status unmistakable regardless of which status it is.
- Express the journey's sequence and win/lose fork visually so users can locate and tap their real status quickly.
- Keep the change frontend-only: no proto/backend/BSR/enum changes.
- Preserve existing behavior: any status freely settable, auth-gated visibility, immediate dashboard-badge reflection, "stop tracking" removal.
- Improve accessibility (single-select semantics, non-color cues).

**Non-Goals:**
- Enforcing transition rules / a state machine (backend explicitly allows any transition; UI must not block transitions).
- Changing the `TicketJourneyStatus` enum, RPCs, or storage.
- Fixing the `JP-13` venue-label bug (separate `fix-event-detail-venue-label` change).
- Restyling the dashboard card badge (noted as optional consistency follow-up only).

## Decisions

### D1: Two-phase layout (process / outcome)

Split the five statuses into **① 申込フロー** (`TRACKING ▸ APPLIED`, horizontal segment) and **② 結果** (outcome). This mirrors the two semantic phases of the DAG: a neutral pre-result process, then a mutually-exclusive result.

- **Alternative considered — keep one flat row:** rejected; it is the source of the current UX problem and cannot express the fork.
- **Alternative considered — horizontal flowchart with branch arrows:** rejected for a ~340px bottom sheet; five nodes + arrows cramp tap targets and shrink labels.

### D2: Outcome as a vertical stack, success on top (Good is Up)

In ② 結果, stack the routes vertically: the **当選 success route on top** (`UNPAID → PAID` vertical mini-flow), the **`LOST` failure route below and de-emphasized**.

- **Rationale:** The "Good is Up" conceptual metaphor (Lakoff & Johnson; Meier & Robinson 2004) is robust and cross-cultural — far stronger than horizontal valence. Horizontal left/right valence is weak and handedness-dependent (Casasanto's body-specificity hypothesis), so an earlier "lost-left / won-right" idea was rejected as ungrounded. Vertical stacking also de-emphasizes failure (UX convention: do not give error/failure states equal visual weight) and, practically, gives each route the full sheet width — larger tap targets, no side-by-side cramping at 340px.
- **Alternative considered — side-by-side `LOST` | 当選:** rejected; gives failure equal billing and cramps the win route's two sub-states.

### D3: Cumulative progress derived from the single stored status

The stored data is one status, but the DAG is fixed, so the path-to-here is derivable. Render passed states as completed (`✓`, low-emphasis), the current state as the sole solid-filled node, and future states as outlined.

Derivation (pure view-model logic in the `.ts`):

| Current status | Completed (✓) | Current (solid) | Dimmed (exclusive) |
|----------------|---------------|-----------------|--------------------|
| `TRACKING` | — | TRACKING | 結果 section (結果待ち) |
| `APPLIED` | TRACKING | APPLIED | 結果 section (結果待ち) |
| `LOST` | TRACKING, APPLIED | LOST | 当選 route |
| `UNPAID` | TRACKING, APPLIED | UNPAID | LOST route |
| `PAID` | TRACKING, APPLIED, UNPAID | PAID | LOST route |

- **Alternative considered — highlight current only (no ✓):** rejected; loses the "where am I in the journey" affordance that motivated the redesign.

### D4: Contrast via fill-vs-outline, not color intensity

Exactly one node is solid-filled (the current state) at any time; everything else is outlined or low-emphasis. This is the structural fix for the visibility problem — the selection reads as "the one filled chip," so it no longer depends on hue saturation or tint opacity surviving against a dark background.

- **Alternative considered — bump the 25% tint to a higher opacity:** rejected as a band-aid; still relies on color intensity and still flattens `LOST`'s muted palette.

### D5: Semantic hue assignment

Hue encodes meaning, not selection:

| Status | Hue (current/solid) | Meaning |
|--------|---------------------|---------|
| `TRACKING`, `APPLIED` | neutral / blue | in-progress, emotionally neutral |
| `LOST` | red (solid → legible even if dark) | failure, terminal |
| `UNPAID` | **amber / orange (highest attention)** | action required — pay now |
| `PAID` | green | success, terminal |

`UNPAID` is deliberately the most attention-grabbing because it is the only state with a pending real-world action. Colors are defined as scoped `oklch()` custom properties consistent with the existing CUBE CSS token approach (`cube/require-token-variables`).

### D6: Outcome gating = visible-but-dimmed, always tappable

Before `APPLIED` is reached, ② 結果 is shown dimmed with a "結果待ち" affordance, but remains tappable. This honors the backend's "any transition allowed" contract (a user may correct/jump) while signaling the natural order.

- **Alternative considered — disable 結果 until APPLIED:** rejected; would contradict the no-state-machine contract and block legitimate self-correction.

### D7: Accessibility — radiogroup

Replace the `button[data-active]` pills with a `role="radiogroup"` containing `role="radio"` options (`aria-checked`), since the control is single-select. Each option carries a non-color cue (icon ✓ / ! / ✕ / ● plus its text label) so meaning survives without color. Maintain ≥44px tap targets (the vertical stack and full-width cards make this natural). The existing `data-testid` hooks for E2E are preserved.

## Risks / Trade-offs

- **[Increased template/CSS complexity vs the simple `repeat.for`]** → Keep the status→view-state mapping (✓ / current / future / dimmed) as small pure getters in the `.ts`, unit-tested per status; the template binds to those rather than computing inline.
- **[Vertical layout adds height to the sheet]** → The sheet already scrolls; the two-phase grouping with full-width rows is acceptable on mobile. Verify against the shortest supported viewport.
- **[Color-only meaning would fail a11y]** → Mandated icon + text cue per state (D7); covered by a spec scenario.
- **[Risk of implying an enforced state machine]** → Copy and gating must read as guidance, not restriction; 結果 stays tappable (D6). Covered by a spec scenario asserting any status remains settable.
- **[Dashboard badge palette could drift from the new sheet palette]** → Out of scope here, but flagged so a later change can align them; tokens are defined centrally to make that cheap.

## Migration Plan

Pure frontend presentation change; no data migration. Ship as a single frontend PR. Rollback = revert the PR (no schema/RPC coupling). Validate via `make check` (Biome + stylelint + typecheck + vitest), updated component unit tests for the view-state derivation, and a manual/visual pass over all five statuses in the bottom sheet. Refresh visual baselines if the frontend visual-regression suite flags the intended UI change.

## Open Questions

- None blocking. The dashboard-badge palette alignment is intentionally deferred to a future change.
