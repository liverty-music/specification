## Context

The `hype-inline-slider` component currently accepts a `hypeLevel: HypeStop` (string union: `'watch' | 'home' | 'nearby' | 'away'`). The parent route converts `HypeType` enum → `HypeStop` string via a method call `hypeStop(artist)`. Aurelia 2 cannot observe property changes inside method calls when the argument reference is stable, causing the UI to not reflect optimistic updates.

## Goals / Non-Goals

**Goals:**
- Fix the reactivity bug so the slider visually updates after hype changes.
- Simplify the data flow by removing the `HypeStop` indirection.
- Use native `<input type="radio">` for accessibility.

**Non-Goals:**
- Redesigning the slider visuals or interaction model.
- Changing backend `SetHype` RPC behavior.
- Modifying the grid view context menu (it binds `contextMenuArtist.hype` directly and already works).

## Decisions

### 1. Component accepts `HypeType` enum directly

The `hype-inline-slider` component will accept `@bindable hype: HypeType` instead of `@bindable hypeLevel: HypeStop`. The component maps `HypeType` values to internal stop indices for rendering.

**Why:** Eliminates the parent-side conversion function that broke reactivity. The template binding `hype.bind="artist.hype"` gives Aurelia a direct property path to observe.

**Alternative considered:** Keep `HypeStop` and fix the template with `hype-level.bind="hypeStop(artist.hype)"`. Rejected because it preserves unnecessary indirection — the `HypeStop` type adds no value over the proto enum.

### 2. Internal stops array uses `HypeType` values

The component's `stops` array changes from `['watch', 'home', 'nearby', 'away']` to `[HypeType.WATCH, HypeType.HOME, HypeType.NEARBY, HypeType.AWAY]`. Template iteration and active-state comparison use enum values directly.

**Why:** No string conversion needed anywhere. The `data-active` check becomes `stop === hype` with both sides being `HypeType`.

### 3. Event detail uses `HypeType` instead of `HypeStop`

The `hype-changed` custom event detail changes from `{ artistId, level: HypeStop }` to `{ artistId, hype: HypeType }`. The parent handler no longer needs `HYPE_FROM_STOP` conversion.

**Why:** Aligns the event contract with the proto enum used everywhere else.

### 4. Native `<fieldset>` + `<input type="radio">` (no ARIA roles)

Use native `<fieldset>` with a visually hidden `<legend>` as the group container. Each stop is a `<label>` wrapping a visually hidden `<input type="radio">` and a visual dot `<span>`. Radio inputs use Aurelia 2's `model.bind`/`checked.bind` pattern. For unauthenticated users, `click` is intercepted with `preventDefault()` to block selection.

**Why:** Per MDN guidance, native HTML radio inputs are preferred over ARIA `role="radiogroup"`/`role="radio"` when no special reason exists to use ARIA. Native radios provide built-in keyboard navigation, focus management, and screen reader support without custom ARIA attributes.

**Alternative considered:** ARIA `role="radiogroup"` on a `<div>` with `role="radio"` buttons. Rejected because native HTML elements provide the same semantics with less code and better browser support.

## Risks / Trade-offs

- **Test updates required** → Tests reference `HypeStop` and `hypeLevel`. Straightforward find-and-replace.
- **CSS `data-level` attribute values change** → CSS selectors use `[data-level="watch"]` etc. These change to `[data-level="1"]` etc. (HypeType enum values). Low risk — contained within the component's scoped CSS.
