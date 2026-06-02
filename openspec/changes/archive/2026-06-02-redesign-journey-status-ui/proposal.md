## Why

The Ticket Status control in `EventDetailSheet` renders the five journey statuses (`TRACKING`, `APPLIED`, `LOST`, `UNPAID`, `PAID`) as a flat horizontal row of pills with no indication of order, branching, or the user's current progress. Two concrete problems result:

- **Poor visibility of the selected state.** The active state is conveyed only by a 25%-opacity background tint over a dark sheet, so the current selection is barely distinguishable from unselected pills — worst for `LOST`, which is intentionally the most muted color.
- **The layout does not match the real acquisition journey.** The statuses form a branching flow (apply → win/lose; win → pay), but the flat row hides the sequence and the win/lose fork, making it hard for users to locate and tap their actual status.

## What Changes

- Replace the flat horizontal pill row with a **two-phase layout** in the Ticket Status section:
  - **① 申込フロー (process):** `TRACKING ▸ APPLIED` as a horizontal segmented progression.
  - **② 結果 (outcome):** a vertical stack with the **success route on top** (`UNPAID → PAID` as a vertical mini-flow under a "当選" heading) and the **failure route (`LOST`) below and de-emphasized**.
- **Cumulative progress display:** states the user has passed through (derived from the single stored status via the known journey DAG) are shown as completed (`✓`), the current state is the sole solid-filled node, and future states are outlined.
- **Outcome gating:** the 結果 section remains always tappable (self-reported), but is visually dimmed ("結果待ち") until `APPLIED` is reached.
- **Mutual exclusivity made visible:** selecting `LOST` dims the win route and vice-versa.
- **Contrast via fill-vs-outline, not color intensity:** exactly one node is solid-filled at a time, so the current selection is unmistakable regardless of hue.
- **Semantic hue assignment:** `UNPAID` = amber/highest-attention (action required), `PAID` = green (success), `LOST` = red (failure), `TRACKING`/`APPLIED` = neutral/blue (in-progress).
- **Accessibility:** the status control becomes a single-select `role="radiogroup"` of `role="radio"` options with `aria-checked`, and every state carries a non-color cue (icon + text label).
- Frontend-only. No proto, backend, or BSR changes — the `TicketJourneyStatus` enum, RPCs, and storage are unchanged.

Out of scope: the `JP-13` raw `adminArea` venue-label bug (handled by the separate `fix-event-detail-venue-label` change).

## Capabilities

### New Capabilities
<!-- None — this change modifies presentation of an existing capability. -->

### Modified Capabilities
- `ticket-journey`: add requirements governing the Ticket Status UI layout, cumulative progress display, outcome gating, visual contrast model, semantic color mapping, and radiogroup accessibility. The existing data model, RPC, and auth-visibility requirements are unchanged.

## Impact

- **Affected code (frontend only):**
  - `src/components/live-highway/event-detail-sheet.html` — replace the `repeat.for` pill row with the two-phase structure and radiogroup semantics.
  - `src/components/live-highway/event-detail-sheet.css` — new fill-vs-outline contrast model, semantic color tokens, two-phase/vertical-stack layout.
  - `src/components/live-highway/event-detail-sheet.ts` — derive cumulative/dim/exclusivity view-state from the current `journeyStatus`; selection still calls the existing `journeyService.setStatus`.
  - `src/locales/{ja,en}/translation.json` — copy for the "当選" group heading and the 申込フロー / 結果 section labels.
- **Unchanged:** `TicketJourneyService` proto/RPC, backend handlers, `ticket_journeys` schema, `TicketJourneyStatus` enum values.
- **Consistency follow-up (optional):** the dashboard card status badge (`event-card.html`) may later adopt the same semantic palette for coherence — noted in design, not required by this change.
