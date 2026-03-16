## Why

Tapping a hype dot on the My Artists slider completes the `SetHype` RPC successfully but the UI does not update. The root cause is that the template binding `hype-level.bind="hypeStop(artist)"` passes the `artist` object reference to a method call; Aurelia 2 observes the reference (which never changes) rather than the mutated `artist.hype` property, so the binding never re-evaluates after an optimistic update.

## What Changes

- Replace the `HypeStop` string intermediary with direct `HypeType` enum binding (`hype.bind="artist.hype"`), making the dependency explicit to Aurelia's observation system.
- Remove `hypeStop()`, `HYPE_TO_STOP`, and `HYPE_FROM_STOP` from the route; the slider component accepts `HypeType` directly and handles conversion internally.
- Add `role="radiogroup"` / `role="radio"` + `aria-checked` accessibility semantics to the slider component.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `hype-inline-slider`: Remove `HypeStop` indirection from the public API; accept `HypeType` directly. Add ARIA radiogroup semantics.

## Impact

- **frontend**: `hype-inline-slider` component (TS, HTML), `my-artists-route` (TS, HTML), and their tests.
- No backend, proto, or infrastructure changes required.
