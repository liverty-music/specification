# Spotlight: CSS Anchor Positioning Hybrid

## HTML (Popover + Visual Spotlight + Click Blockers)

```html
<div popover="manual" class="coach-mark-overlay" ref="overlayEl">
  <div class="visual-spotlight"></div>

  <div class="click-blocker mask-top"></div>
  <div class="click-blocker mask-right"></div>
  <div class="click-blocker mask-bottom"></div>
  <div class="click-blocker mask-left"></div>

  <div class="coach-tooltip">
    <!-- tooltip content -->
  </div>
</div>
```

## CSS

```css
/* View Transition for smooth spotlight movement */
::view-transition-group(spotlight) {
  animation-duration: 0.4s;
  animation-timing-function: cubic-bezier(0.25, 1, 0.5, 1);
}

.coach-mark-overlay {
  /* Popover UA reset */
  margin: 0; border: none; padding: 0;
  width: 100vw; height: 100vh;
  background: transparent;
  pointer-events: none;
  &::backdrop { display: none; }
}

/* Visual layer: box-shadow creates dark overlay with rounded cutout */
.visual-spotlight {
  position: fixed;
  top: anchor(--coach-target top);
  right: anchor(--coach-target right);
  bottom: anchor(--coach-target bottom);
  left: anchor(--coach-target left);
  margin: -8px; /* padding around target */
  border-radius: var(--spotlight-radius, 12px);
  box-shadow: 0 0 0 100vmax color-mix(in oklch, oklch(0% 0 0) 70%, transparent);
  pointer-events: none;
  view-transition-name: spotlight;
}

/* Logic layer: transparent divs block clicks outside target */
.click-blocker {
  position: fixed;
  background-color: transparent;
  pointer-events: auto;
}
.mask-top    { inset: 0 0 auto 0; bottom: anchor(--coach-target top); }
.mask-bottom { inset: auto 0 0 0; top: anchor(--coach-target bottom); }
.mask-left   { top: anchor(--coach-target top); bottom: anchor(--coach-target bottom); left: 0; right: anchor(--coach-target left); }
.mask-right  { top: anchor(--coach-target top); bottom: anchor(--coach-target bottom); right: 0; left: anchor(--coach-target right); }

/* Tooltip positioned via Anchor Positioning */
.coach-tooltip {
  position: fixed;
  position-anchor: --coach-target;
  position-area: block-end;
  position-try-fallbacks: flip-block, flip-inline;
  margin-top: 1rem;
  pointer-events: auto;
}

@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(spotlight) { animation-duration: 0s; }
}
```

## JS (Anchor-name reassignment with View Transition)

```typescript
// Assign anchor-name to target (activates CSS positioning)
public highlight(newTarget: HTMLElement) {
  document.startViewTransition(() => {
    this.currentTarget?.style.removeProperty('anchor-name');
    newTarget.style.anchorName = '--coach-target';
    this.currentTarget = newTarget;
  });
}

// Cleanup
public deactivate() {
  this.currentTarget?.style.removeProperty('anchor-name');
  this.currentTarget = null;
  this.overlayEl.hidePopover();
}
```

## Key Points

- `anchor-name` on target element drives all positioning via CSS — no `getBoundingClientRect()`
- `box-shadow: 0 0 0 100vmax` on `.visual-spotlight` creates the dark overlay with cutout
- `border-radius: var(--spotlight-radius)` controls cutout shape (50% for circles, 12px for cards)
- 4 transparent click-blockers handle tap interception without affecting visual layer
- `view-transition-name: spotlight` enables smooth slide animation between targets
- `popover="manual"` places overlay on top layer — no z-index management needed
