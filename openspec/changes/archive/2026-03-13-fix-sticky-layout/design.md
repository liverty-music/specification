## Context

`my-app` uses a two-row CSS Grid (`1fr` / `min-content`) with `block-size: 100dvh`. The `<main>` element has `display: contents`, so `au-viewport` becomes a direct grid participant. However, five overlay custom elements sit between `<main>` and `<bottom-nav-bar>` in DOM order. Although four of them have `block-size: 0`, they still occupy implicit grid rows, displacing `bottom-nav-bar` from row 2 to row 7. Additionally, `coach-mark` was never included in the collapse list.

Current DOM order inside `my-app`:
1. `au-viewport` (via `main { display: contents }`)
2. `pwa-install-prompt` — implicit row
3. `notification-prompt` — implicit row
4. `toast-notification` — implicit row
5. `error-banner` — implicit row
6. `coach-mark` — implicit row (no collapse styling at all)
7. `bottom-nav-bar` — should be row 2, actually row 7

## Goals / Non-Goals

**Goals:**
- `bottom-nav-bar` occupies the explicit `min-content` grid row and stays pinned at viewport bottom.
- `live-highway`'s scroll container is properly height-constrained so `position: sticky` works on the stage header and date separators.
- Overlay elements are completely removed from grid flow.

**Non-Goals:**
- Changing the HTML structure or DOM order.
- Modifying overlay component internals — they already use top-layer APIs correctly.
- Addressing any other layout issues beyond the sticky/fixed positioning bug.

## Decisions

### Use `position: fixed` + `inset: 0` instead of `block-size: 0` collapse

**Choice**: Replace the current `overflow: hidden; display: block; block-size: 0` pattern with `position: fixed; inset: 0`.

**Why**: `position: fixed` removes elements from normal flow entirely — they no longer participate in grid row creation. The current `block-size: 0` approach keeps them in flow (they're still grid items with 0-height implicit rows), which is the root cause. Since these elements use popover/dialog top-layer APIs, their visual rendering is independent of their flow position.

**Alternative considered**: Using `position: absolute` — also removes from flow but requires a positioned ancestor. `fixed` is simpler and more predictable for elements that render in the top layer anyway.

**Alternative considered**: Explicit `grid-row` placement on `au-viewport` and `bottom-nav-bar` — works around the symptom but leaves unnecessary implicit rows in the grid. Less clean.

### Add `coach-mark` to the overlay exclusion list

It was omitted from the original list. It uses the popover API just like the other overlays and should receive identical treatment.

## Risks / Trade-offs

- **[Low] Overlay pointer events**: `position: fixed; inset: 0` creates a full-viewport box. Must keep `pointer-events: none` (or equivalent) so it doesn't intercept clicks. Current `overflow: hidden; block-size: 0` already prevents interaction, but we need to verify this is maintained. → Mitigation: The elements render via top-layer popover/dialog which handles its own pointer events; the fixed-positioned box just needs to not block.
- **[Low] Aurelia ref binding**: The existing comment notes `display: contents` breaks Aurelia ref bindings. `position: fixed` preserves the box, so this remains safe.

### Implementation note

The final implementation retains both `position: fixed` and `overflow: hidden; block-size: 0` as a defensive measure. While `position: fixed` alone is sufficient for flow removal, the `block-size: 0` provides a fallback for any edge case where the fixed positioning might not apply.
