## Context

The My Artists page renders a `<table>` with 6 columns: artist name, 4 hype-level radio dots, and a trash icon button. On mobile (touch) devices, the trash column occupies ~48px that could widen the hype slider area. The existing `unfollowArtist()` method and View Transitions are already in place — this change adds a swipe gesture as an additional trigger.

Key constraints:
- `<table>` structure must not change (semantic HTML, screen reader accessibility)
- `<tr>` elements are `display: table-row` — `overflow: hidden` and `transform` cannot be applied directly
- The vertical scroll container is `artists-fieldset` (`overflow-y: auto`) — swipe must not interfere with vertical scrolling
- No new npm packages — Pointer Events API and WAAPI are available in all target browsers

## Goals / Non-Goals

**Goals:**
- On touch devices: hide trash column, giving hype dots more horizontal space
- Add left-swipe gesture on artist rows that calls the existing `unfollowArtist()` method
- Snap back on release if threshold not reached (with spring-like WAAPI animation)
- Preserve keyboard and screen reader access to the unfollow action
- Implement as a reusable Aurelia 2 Custom Attribute

**Non-Goals:**
- Swipe on non-touch (pointer: fine) devices — trash icon remains
- Custom swipe velocity physics (distance threshold only)
- Right-swipe or any other gesture direction
- Changes to the unfollow confirmation/undo toast logic

## Decisions

### 1. Pointer Events API over Touch Events

**Decision**: Use `pointerdown` / `pointermove` / `pointerup` / `pointercancel` with `setPointerCapture()`.

**Why**: Touch Events require `passive: false` to call `preventDefault()` and don't unify mouse/stylus. `setPointerCapture()` ensures tracking continues even if the pointer moves outside the `<tr>` boundary — critical for a reliable swipe feel. `pointercancel` handles the case where the browser takes over scrolling.

**Alternative considered**: HammerJS / gesture library — rejected (adds a package dependency, overkill for a single gesture).

### 2. Animate inner cell wrappers, not `<tr>`

**Decision**: Each `<td>` / `<th>` gets an inner `<div class="cell-inner">` that is translated via WAAPI. The `<tr>` itself is never transformed.

**Why**: `display: table-row` elements do not reliably support `transform` in all browsers. Moving inner wrappers sidesteps this entirely while keeping the table structure intact.

**Alternative considered**: Wrapping rows in a `position: relative` container and using absolute positioning — rejected (breaks table layout).

### 3. `touch-action: pan-y` for scroll/swipe coexistence

**Decision**: Set `touch-action: pan-y` on `.artist-row` via CSS.

**Why**: This tells the browser to handle vertical pan natively, so the `pointermove` handler only fires after the gesture is confirmed horizontal. This avoids the direction-detection lock-in logic and makes the interaction feel native.

**Direction lock**: On the first `pointermove`, compute `|dx|` vs `|dy|`. If `|dy| > |dx|`, release pointer capture and bail — let the browser scroll. Only commit to swipe when `|dx| > |dy| * 1.5`.

### 4. `@media (pointer: coarse)` to hide trash column

**Decision**: Use the CSS media query `(pointer: coarse)` to `display: none` the `.artist-unfollow-col` and its header.

**Why**: This is a CSS-only, no-JS approach that correctly identifies touch-primary devices. On mixed-input devices (e.g. Surface), `pointer: fine` keeps the button visible.

**Border-radius fix**: When the trash column is hidden, `.hype-col:last-child` inside `.artist-row` needs the `border-end-end-radius` / `border-start-end-radius` rules that currently live on `td:last-child`.

### 5. Aurelia 2 Custom Attribute

**Decision**: Implement as `swipe-to-delete` Custom Attribute that accepts a `callback` bindable.

```html
<tr swipe-to-delete.bind="{ callback: () => unfollowArtist(artist) }">
```

**Why**: Keeps gesture logic out of the route ViewModel, makes it reusable (e.g., future artist discovery list), and follows the existing codebase pattern of encapsulating cross-cutting concerns in components/attributes.

### 6. Threshold: 40% of row width

**Decision**: Trigger unfollow when `dx > rowWidth * 0.4`.

**Why**: 40% is enough to feel intentional without being exhausting. Below threshold, WAAPI `reverse()` snaps back. Above threshold, animate to full width exit, then call `callback()` which triggers the existing View Transition.

## Risks / Trade-offs

- **`pointer: coarse` heuristic is imperfect** → Devices with both mouse and touch report `pointer: fine` (coarse is the secondary pointer). On such devices the trash icon stays visible and swipe is disabled. This is acceptable — the primary use case is phone/tablet. Mitigation: none needed.

- **`cell-inner` wrapper adds DOM nodes** → 6 extra `<div>` elements per row. With typical artist counts (10-50), this is negligible. Mitigation: only add wrappers when `pointer: coarse` is detected (via JS check at attribute bind time).

- **WAAPI `reverse()` can be janky on low-end Android** → The snap-back animation involves reversing a running animation. Mitigation: use a short duration (200ms) and `easing: 'ease-out'` so jank is barely perceptible.

- **`pointercancel` during scroll mid-swipe** → If a user starts swiping and the browser decides to scroll, `pointercancel` fires. Must reset transform to 0 immediately (no animation) to avoid a stuck row. This is handled by the `pointercancel` listener.

## Migration Plan

Pure frontend change, no deployment coordination needed:
1. Implement and merge — ships in next frontend deploy
2. No rollback strategy needed (CSS media query and JS are self-contained)

## Open Questions

- Should the swipe reveal a red "Delete" label behind the row (iOS-style), or just a directional arrow? → Start without it for simplicity; can be added as visual polish later.
- Should swipe work on the empty-state row? → N/A, no rows in empty state.
