## Context

The Concert Highway component renders two visual layers for hype-matched events:

- **Layer A** — viewport-fixed triangular laser beam overlay (`.beam-overlay` / `.laser-beam`) rendered in `concert-highway.html`
- **Layer B** — card-level spotlight effect via `[data-matched]` CSS selector in `event-card.css`

Layer B is working correctly. Layer A is invisible.

The `.beam-overlay` uses `position: fixed; inset: 0` to span the full viewport. However, its parent `concert-highway` has `:scope { overflow: hidden }`. In modern browsers (Chrome 103+, Safari 15.4+), an ancestor element with `overflow: hidden` combined with `position: relative` can act as a containing block for `position: fixed` descendants, clipping them to the ancestor's bounds. Since the beams have `block-size: var(--beam-h, 0)` with default `0`, and the containing block is `concert-highway` (not the viewport), the beams render but are clipped to zero height.

Additionally, `concert-highway[data-blurred="true"] { filter: blur(4px) }` in `dashboard-route.css` would also break `position: fixed` containment (filter creates a new stacking context), though this only affects the blurred onboarding state.

The scroll overflow is fully handled by `.concert-scroll { overflow-block: auto; overflow-inline: hidden }`, so `overflow: hidden` on `:scope` is redundant.

## Goals / Non-Goals

**Goals:**
- Make Layer A laser beams visible across the full viewport for hype-matched events
- No regressions in card layout, scroll behaviour, or header positioning

**Non-Goals:**
- Fixing the `filter: blur` containment issue (the blurred state is intentional and beam visibility during blur is not required)
- Changing beam positioning logic or the `updateBeamPositions()` algorithm

## Decisions

### Remove `overflow: hidden` from `concert-highway :scope`

**Decision**: Delete the `overflow: hidden` declaration from `:scope` in `concert-highway.css`.

**Why**: `.concert-scroll` already declares `overflow-block: auto; overflow-inline: hidden`, which handles all scroll clipping. The `:scope`-level overflow is defensive/redundant and is the direct cause of the `position: fixed` containment issue.

**Alternative considered**: Move `.beam-overlay` outside `concert-highway` (portal pattern). Rejected — would require significant refactoring of `updateBeamPositions()` DOM queries and `getBeamIndex()` cross-component communication with no additional benefit.

**Alternative considered**: Change `.beam-overlay` from `position: fixed` to `position: absolute` with `inset: 0` on a full-height container. Rejected — beams need to stay fixed relative to the viewport during scroll to produce the correct visual effect.

## Risks / Trade-offs

- **[Risk] Content overflow**: Without `:scope` overflow clipping, some child element could theoretically overflow `concert-highway`. → **Mitigation**: `.concert-scroll` clips its own content; the stage header is contained within the grid. Visual regression testing covers this.
- **[Risk] `filter: blur` still breaks beams**: `dashboard-route.css` applies `filter: blur(4px)` to `concert-highway` during the onboarding region-selection state. During this state, `position: fixed` children are still contained. → **Accepted**: Beams are not needed while the UI is blurred (it's a blocking modal state).
