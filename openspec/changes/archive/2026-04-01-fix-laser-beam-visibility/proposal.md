## Why

The viewport-fixed laser beam overlay (Layer A) in the Concert Highway is not visible on hype-matched event cards in the dashboard. The root cause is a CSS containment issue: `concert-highway` has `overflow: hidden` on its `:scope`, which in modern browsers clips `position: fixed` children to the element's bounds, preventing the beam overlay from rendering across the full viewport.

## What Changes

- Remove `overflow: hidden` from `concert-highway`'s `:scope` rule — scroll clipping is already handled by `.concert-scroll`'s own `overflow-block: auto; overflow-inline: hidden`
- Verify that removing `:scope` overflow does not cause visual regressions (cards, headers, or beams overflowing unexpectedly)

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `concert-highway`: Laser beam overlay now renders correctly across the full viewport for hype-matched events

## Impact

- `frontend/src/components/live-highway/concert-highway.css` — single-line removal
- Visual regression risk: low; `.concert-scroll` retains its own overflow clipping
- No API, proto, or backend changes required
