## Context

The PWA install FAB (`pwa-install-fab`) is a circular button fixed to the bottom-right corner. Its CSS lives entirely in `pwa-install-fab.css` under `@layer block { @scope (pwa-install-fab) { ... } }`.

Current idle state:
```css
box-shadow:
    0 0 10px oklch(from var(--_glow-color-from) l c h / 35%),
    0 0 20px oklch(from var(--_glow-color-to)   l c h / 20%);
```
This is a static, non-animated shadow. The `signup-prompt-banner` uses an animated `cta-glow` keyframe (2.5s, ease-in-out, infinite) pulsing between low and high opacity box-shadows. The same pattern should be applied here.

The icon (`.pwa-fab-icon`) is currently `1.25rem × 1.25rem`. It can be enlarged to `1.5rem` without changing the button container size (`--_size: 2.75rem`), since the container has `display: flex; align-items: center; justify-content: center`.

## Goals / Non-Goals

**Goals:**
- Make the FAB icon larger and more legible
- Add a pulsing neon border/glow animation that attracts attention in idle state
- Reuse existing design tokens (`--_glow-color-from`, `--_glow-color-to`)
- Fix `aria-hidden="false"` anti-pattern and add `tabindex` control

**Non-Goals:**
- Changing button size or position
- Adding new animations to the entry/ripple sequence
- Changing the icon itself or the iOS instruction sheet
- Refactoring `show.bind` → `if.bind` (separate concern)

## Decisions

### Use `box-shadow` spread-radius to simulate a neon border

**Decision**: Use a multi-layer `box-shadow` where the first layer has `spread-radius: 2px` to act as a visible "border ring", followed by blur layers for the glow. Animate these with a `pwa-fab-neon-pulse` keyframe.

**Why**: `border-image` does not work with `border-radius: full`. A `border` with solid color would override the entry animation and look flat. `box-shadow` with `0 0 0 2px` (no blur, with spread) produces a crisp ring that visually reads as a border.

**Keyframe naming**: Follow the existing `pwa-fab-*` prefix convention in the file:
- `pwa-fab-enter` (existing)
- `pwa-fab-ripple` (existing)
- `pwa-fab-fade` (existing, reduced-motion)
- `pwa-fab-neon-pulse` (new)

**Pulse keyframe**:
```css
@keyframes pwa-fab-neon-pulse {
    0%, 100% {
        box-shadow:
            0 0 0 2px oklch(from var(--_glow-color-from) l c h / 50%),
            0 0 10px oklch(from var(--_glow-color-from) l c h / 30%),
            0 0 22px oklch(from var(--_glow-color-to)   l c h / 15%);
    }
    50% {
        box-shadow:
            0 0 0 2px oklch(from var(--_glow-color-from) l c h / 90%),
            0 0 16px oklch(from var(--_glow-color-from) l c h / 55%),
            0 0 32px oklch(from var(--_glow-color-to)   l c h / 30%);
    }
}
```

**Applied via comma-joined `animation` shorthand** (single property, readable):
```css
animation:
    pwa-fab-enter 400ms ease-out both,
    pwa-fab-neon-pulse 2.5s ease-in-out 400ms infinite;
```

### Reduced motion block must explicitly suppress pulse

The `prefers-reduced-motion: reduce` block overrides `.pwa-fab { animation }` with `pwa-fab-fade`. Since this replaces the animation shorthand, `pwa-fab-neon-pulse` is automatically removed. However, a static `box-shadow` fallback must be restored in the same block so the button retains visual definition:

```css
@media (prefers-reduced-motion: reduce) {
    .pwa-fab {
        animation: pwa-fab-fade 300ms ease-out both;
        /* Static fallback — pulse suppressed */
        box-shadow:
            0 0 0 2px oklch(from var(--_glow-color-from) l c h / 50%),
            0 0 10px oklch(from var(--_glow-color-from) l c h / 30%),
            0 0 22px oklch(from var(--_glow-color-to)   l c h / 15%);
    }
    ...
}
```

### Pause pulse animation on focus-visible

The neon pulse `box-shadow` animates opacity. When the button receives keyboard focus, the `focus-visible` outline renders on top but the animating shadow can visually compete with it. Pausing the animation on focus makes the outline clearly readable:

```css
&:focus-visible {
    outline: 2px solid var(--color-brand-accent);
    outline-offset: 5px;  /* widened from 3px to clear the pulse ring */
    animation-play-state: paused;
}
```

### Fix `aria-hidden` anti-pattern and add `tabindex` control

`aria-hidden="false"` does not expose an element to AT — it is a no-op. The correct pattern is to omit the attribute entirely when the element should be visible to AT. Since `show.bind` keeps the button in the DOM, `tabindex` must also be controlled so hidden state removes the button from the tab order:

```html
<button
  show.bind="isVisible"
  aria-hidden.bind="isVisible ? null : 'true'"
  tabindex.bind="isVisible ? '0' : '-1'"
  ...
```

### Icon size: 1.25rem → 1.5rem

**Decision**: Change `.pwa-fab-icon { inline-size: 1.5rem; block-size: 1.5rem; }`.

**Why**: The current 20px icon leaves significant padding inside the 44px button. 24px (1.5rem) fills the container more proportionally and improves tap target legibility. No layout changes needed.

## Risks / Trade-offs

- **[Risk] Animation competes with entry ripple**: Adding `pwa-fab-neon-pulse` with `400ms` delay means it starts as the entry animation finishes. → **Mitigation**: Comma-joined `animation` shorthand with explicit delay handles sequencing cleanly.
- **[Risk] `prefers-reduced-motion` loses box-shadow entirely**: Replacing `animation` removes the animated shadow but does not restore a static one. → **Mitigation**: Explicitly re-declare `box-shadow` in the reduced-motion block.
- **[Risk] Visual noise on low-end devices**: Three simultaneous animations (entry, ripple, pulse). → **Accepted**: The ripple runs only twice and stops; the pulse is the only looping animation in idle state.
