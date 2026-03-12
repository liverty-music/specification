## Context

The concert detail sheet (`event-detail-sheet`) uses `<dialog popover="manual">` to display concert information as a bottom sheet. Two bugs exist:

1. **Onboarding Step 4 deadlock**: The coach mark popover enters the top layer BEFORE the detail sheet popover. LIFO stacking places the detail sheet on top, hiding the coach mark. The user cannot reach the My Artists tab and the tutorial is stuck.

2. **Broken backdrop dismiss (all users)**: The Popover API UA stylesheet enforces `[popover]::backdrop { pointer-events: none !important }`. Clicks on the dark backdrop area pass through to whatever is below, never reaching the `<dialog>` element (which only covers the bottom portion via `inset: auto 0 0`). The `onBackdropClick` handler is effectively dead code.

Current dismiss mechanisms on mobile: only swipe-down works. No Escape key, no backdrop tap, no Android back button support.

## Goals / Non-Goals

**Goals:**

- Fix the onboarding Step 4 stacking order so the coach mark renders above the detail sheet
- Provide working light dismiss for the detail sheet outside onboarding (tap-outside, Escape, Android back)
- Handle browser back navigation when the detail sheet has pushed a history entry
- Use Web Platform primitives (Popover API `auto` mode) instead of reimplementing dismiss logic

**Non-Goals:**

- Changing the onboarding Step 4 flow design (detail sheet open + non-dismissible is intentional)
- Adding CloseWatcher polyfill for Safari (Safari lacks CloseWatcher but `popover="auto"` provides Escape handling natively)
- Changing the coach mark component's fundamental architecture

## Decisions

### Decision 1: Use `popover="auto"` for normal mode, `popover="manual"` for onboarding Step 4

**Choice**: Dynamically switch the popover attribute based on onboarding state.

**Rationale**: `popover="auto"` provides free light dismiss (click-outside, Escape, browser-integrated CloseWatcher for Android back) without manual reimplementation. During onboarding Step 4, the spec requires the sheet to be non-dismissible, so `popover="manual"` is correct there.

**Alternatives considered**:

- *Keep `manual` + expand `<dialog>` to `inset: 0`*: Works for backdrop tap, but requires manual Escape listener and has no Android back button support without CloseWatcher (not available in Safari). More code for less platform benefit.
- *Always use `auto`*: Can't prevent dismiss during onboarding Step 4.

**Implementation**: Aurelia 2 `@bindable` controls the popover mode. The `open()` method reads onboarding state to decide which mode to use before calling `showPopover()`. Since the `popover` attribute must be set before `showPopover()` is called, set it in the `open()` method.

### Decision 2: Re-show coach mark popover after detail sheet opens (top-layer re-ordering)

**Choice**: Add a `bringToFront()` method to the coach mark that calls `hidePopover()` then `showPopover()`, re-inserting it at the top of the LIFO stack.

**Rationale**: The Popover API top layer uses LIFO ordering. The only way to move an existing popover to the top is to hide and re-show it. This is the platform-native approach.

**Alternatives considered**:

- *Open detail sheet first, then coach mark*: Would require delaying the coach mark activation until after the detail sheet's `showPopover()` call. This is fragile because the card click triggers both the detail sheet open (via event-card click propagation) and the tutorial callback synchronously in `onTargetClick`. Splitting this into an async sequence risks race conditions.
- *Use CSS `z-index` on top-layer items*: Not possible. Items in the top layer don't participate in normal z-index stacking — order is strictly LIFO.

**Implementation**: Dashboard's `onTutorialCardTapped()` calls `onboarding.activateSpotlight(...)` which eventually triggers `showPopover()` on the coach mark. Add coordination: after the detail sheet opens, the coach mark calls `bringToFront()`. The onboarding service exposes a `bringSpotlightToFront()` method that the dashboard calls after confirming the detail sheet is open.

### Decision 3: Add `popstate` listener for browser back navigation

**Choice**: Listen for `popstate` in the detail sheet and close when the user navigates back.

**Rationale**: `event-detail-sheet.open()` calls `history.pushState(...)` to update the URL to `/concerts/:id`. When the user presses the browser back button, a `popstate` event fires. Without a listener, the URL changes but the popover stays open, creating a URL/UI mismatch.

**Implementation**: Add `popstate` listener in `open()`, remove in `close()`. The listener calls `close()` but skips the `history.replaceState` call (since the browser already navigated back). Add a flag `closedByPopstate` to differentiate.

### Decision 4: Remove manual Escape key listener

**Choice**: Remove the `document.addEventListener('keydown', this.onKeyDown)` from event-detail-sheet.

**Rationale**: `popover="auto"` handles Escape natively. For `popover="manual"` during onboarding, Escape should NOT close the sheet (spec: non-dismissible). The manual listener is no longer needed in either mode.

**Implementation**: Delete `onKeyDown` property, remove `addEventListener`/`removeEventListener` calls in `open()`/`close()`/`detaching()`.

## Risks / Trade-offs

**[Risk] `popover="auto"` auto-closes when another `auto` popover opens**
The coach mark uses `popover="manual"`, so opening the coach mark won't auto-close an `auto` detail sheet. However, if any future component uses `popover="auto"`, it could close the detail sheet unexpectedly.
→ Mitigation: The coach mark is `manual` and no other `auto` popovers exist currently. Document this constraint.

**[Risk] `bringToFront()` causes a brief visual flicker (hide → show)**
→ Mitigation: Wrap the hide/show in `requestAnimationFrame` or `document.startViewTransition` to batch the repaint. The coach mark's `::backdrop` is `display: none` so there's no backdrop flash. The visual spotlight uses CSS Anchor Positioning which repositions instantly.

**[Risk] `popstate` listener might fire unexpectedly**
→ Mitigation: Check `this.isOpen` before calling `close()`. Remove listener in `close()` to prevent double-firing.

**[Trade-off] Dynamic `popover` attribute switching adds complexity**
The popover attribute is set before each `showPopover()` call. This is a one-line conditional, not a major complexity increase. The benefit (platform-native dismiss) outweighs the cost.
