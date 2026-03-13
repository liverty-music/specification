## Context

The CUBE CSS exception layer prescribes `data-*` attributes for state-driven styling. The `modern-css-platform` spec already requires `data-state` for animation state and `transitionend` for post-animation cleanup. However, the codebase still has 13+ instances of TS/CSS responsibility leaks identified in the `improve-css-design` audit: 3 inline style bindings, 3 class ternaries, 5 setTimeout-based animation orchestrations, and 2 unnecessary `if.bind` for visual state.

## Goals / Non-Goals

**Goals:**
- Establish a clear contract: TS sets `data-*` attributes and CSS custom properties; CSS reads them for styling
- Eliminate all `setTimeout` calls that duplicate CSS animation/transition durations
- Create Aurelia custom attributes for recurring data-state patterns
- Ensure animation durations live in CSS only (single source of truth)

**Non-Goals:**
- Changing the visual design of any component
- Adding new animations or transitions
- Refactoring component architecture or state management
- Adding Container Queries, View Transitions, or Scroll-driven Animations (that's `css-modern-patterns`)

## Decisions

### Decision 1: CSS custom properties for continuous values, data-* for discrete states

Two distinct patterns based on value type:
- **Continuous values** (offsets, colors, dimensions): Pass via `style="--_prop: ${value}"` — CSS reads via `var(--_prop, fallback)`. Use the `--_` prefix convention (component-local custom property).
- **Discrete states** (active/inactive, entering/exiting): Pass via `data-state="${value}"` — CSS reads via `[data-state="active"]`.

**Alternative**: Use `data-*` for everything. Rejected because `data-*` attributes are strings and clumsy for pixel values that change every frame (gestures).

### Decision 2: Aurelia custom attribute for state binding

Create a `state-attr` custom attribute that binds a boolean TS property to a `data-state` attribute:

```html
<div state-attr="active.bind: isActive; variant.bind: currentVariant">
```

This eliminates repetitive ternary patterns in templates. The custom attribute sets `data-state="active"` and `data-variant="${currentVariant}"` on the host element.

**Alternative**: Keep explicit `data-state="${ternary}"` in templates. Acceptable for one-off cases but DRY violation for the 10+ components that use this pattern.

### Decision 3: animationend/transitionend for animation lifecycle

Replace `setTimeout(() => cleanup(), DURATION_MS)` with:
```typescript
element.addEventListener('transitionend', (e) => {
  if (e.propertyName !== 'opacity') return
  cleanup()
}, { once: true })
```

For `prefers-reduced-motion`, detect via `matchMedia('(prefers-reduced-motion: reduce)')` and run cleanup immediately since no transition fires.

**Alternative**: Keep setTimeout as fallback alongside event listener. Rejected because it creates race conditions. The CSS event is the authoritative signal.

### Decision 4: Remove if.bind where Popover API manages visibility

For `celebration-overlay` and `coach-mark`, remove `if.bind="visible"` and rely on the Popover API's `showPopover()`/`hidePopover()` which manages top-layer visibility natively. CSS handles transitions via `[data-state]`.

## Risks / Trade-offs

- [Risk] Gesture-driven transforms (swipe, drag) update `--_offset` every frame via style binding → This is acceptable; CSS custom properties on `style=` are the standard pattern for frame-by-frame updates. No alternative avoids this.
- [Risk] `transitionend` may not fire if element is removed before transition completes → Use `{ once: true }` and ensure element remains in DOM during transition (if.bind removal helps here).
- [Risk] The `state-attr` custom attribute adds a new Aurelia dependency → Keep it simple (< 30 lines), no external deps, tested via unit test.
