# Coach Mark: Inline SVG Arrow with Drawing Animation

## HTML (Aurelia `switch.bind` for direction)

```html
<div class="coach-arrow" switch.bind="arrowDirection">
  <svg case="up" viewBox="0 0 100 100" fill="none" stroke="currentColor">
    <path class="arrow-line" d="M10,90 Q50,90 90,20" />
    <path class="arrow-head" d="M70,20 L90,20 L90,40" />
  </svg>
  <svg case="down" viewBox="0 0 100 100" fill="none" stroke="currentColor">
    <path class="arrow-line" d="M10,10 Q50,10 90,80" />
    <path class="arrow-head" d="M70,80 L90,80 L90,60" />
  </svg>
</div>
```

## CSS

```css
.coach-arrow svg {
  width: 80px;
  height: 80px;
  stroke-width: 4px;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: drop-shadow(0 4px 6px color-mix(in oklch, oklch(0% 0 0) 50%, transparent));
  transform: rotate(-5deg); /* slight tilt for hand-drawn feel */
}

/* Line draws in over 600ms */
.arrow-line {
  stroke-dasharray: 150;
  stroke-dashoffset: 150;
  animation: draw-line 0.6s cubic-bezier(0.25, 1, 0.5, 1) forwards;
}

/* Arrowhead fades in after line finishes */
.arrow-head {
  opacity: 0;
  animation: fade-in-head 0.3s ease-out 0.6s forwards;
}

@keyframes draw-line {
  to { stroke-dashoffset: 0; }
}

@keyframes fade-in-head {
  to { opacity: 1; }
}

@media (prefers-reduced-motion: reduce) {
  .arrow-line { animation: none; stroke-dashoffset: 0; }
  .arrow-head { animation: none; opacity: 1; }
}
```

## Key Points

- `stroke="currentColor"` inherits tooltip text color — auto-adapts to theme changes
- `stroke-dasharray`/`stroke-dashoffset` creates the "drawing" animation without JS
- `switch.bind` selects SVG path based on tooltip position relative to target
- Up arrow: curved path from bottom-left to top-right (tooltip below target)
- Down arrow: curved path from top-left to bottom-right (tooltip above target)
- `transform: rotate(-5deg)` adds organic hand-drawn feel
