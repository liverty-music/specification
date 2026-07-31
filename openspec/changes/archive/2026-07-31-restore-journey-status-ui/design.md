## Context

Commit `0245f03` deleted HTML template content from two components while leaving all backing layers intact:
- `EventCard` ViewModel: `journeyConfig` getter (reads from `JOURNEY_STATUS_CONFIG_MAP`)
- `EventDetailSheet` ViewModel: full journey state machine (`status`, `nodeStates`, `setJourneyStatus`, `removeJourney`, `onJourneyKeydown`, `outcomePending`, `successDimmed`, `failureDimmed`)
- `event-card.css`: `.journey-badge` styles
- `event-detail-sheet.css`: all `.sheet-journey`, `.journey-node`, `.journey-phase` styles
- `TicketJourneyStore`: observable `journeyMap`, `load`, `setStatus`, `delete`
- Backend `TicketJourneyService`: deployed and operational

The only missing pieces are the HTML binding points in the two template files.

## Goals / Non-Goals

**Goals:**
- Restore the journey badge `<span>` in `event-card.html` so the card corner shows the user's current status icon
- Restore the full `<section class="sheet-journey">` block in `event-detail-sheet.html` so authenticated users can set/update/remove their journey status from the concert detail sheet
- Satisfy the existing requirements in `ticket-journey` and `journey-status-presentation` specs

**Non-Goals:**
- Restoring the Tickets bottom-nav tab (`path: 'tickets'`) — that tab leads to the ZK proof entry feature which is a separate, unrelated capability
- Any changes to ViewModel logic, CSS, services, backend, or proto
- New unit or E2E tests — existing `EventDetailSheet` spec already covers journey store interaction

## Decisions

### Exact revert of deleted HTML

The deleted HTML is restored verbatim from `0245f03`. No redesign is needed because:
- The ViewModel API is identical to what the template was calling
- The CSS classes are still defined in `event-detail-sheet.css` and `event-card.css`
- i18n keys (`eventDetail.ticketStatus`, `eventDetail.journeyPhase.*`, `eventDetail.journeyStatus.*`, `eventDetail.stopTracking`) are still present

Restoring verbatim minimises diff noise and avoids reintroducing regressions.

### Insertion position in event-detail-sheet.html

The journey `<section>` is inserted between the closing `</section>` of `.sheet-details` and the opening `<footer class="sheet-actions">`. This matches the original layout order and the CSS `border-block-start` separator on `.sheet-journey` that creates a visual divider from the details above.

## Risks / Trade-offs

- **No risk**: The ViewModel, CSS, store, and backend are all intact and tested. The template additions are purely binding existing, verified logic to the DOM.
- **Stale CSS custom properties**: `event-detail-sheet.css` references `--_node-faint` which is derived from per-status tokens. These tokens are defined via `@scope` in the existing CSS, still present, so there is no gap.

## Migration Plan

1. Restore the 8-line journey badge block in `event-card.html`
2. Restore the 128-line journey section block in `event-detail-sheet.html`
3. Run `make check` (lint + unit tests) — no failures expected
4. Open PR against `frontend` → merge → release as a patch version

Rollback: revert the two HTML files to their current state.
