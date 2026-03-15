## Context

The onboarding flow (PR #146) guides unauthenticated users through artist discovery → dashboard → my-artists → signup. The implementation has several interrelated bugs stemming from three root causes:

1. **AuthHook gap**: Routes without `tutorialStep` data fall through to the "not authenticated" branch, triggering an inappropriate toast during onboarding.
2. **Spotlight rendering bug**: The coach mark overlay's own `background` paints over the child spotlight element's `box-shadow` hole, making the cutout invisible.
3. **Progress semantics mismatch**: The progress bar tracks concert search completion (`completedSearchCount / followedCount`) while the guidance message tracks follow progress toward a 3-artist target.

The frontend already uses CSS Anchor Positioning (Baseline 2025) for tooltip placement. The DNA orb canvas uses Canvas 2D with Matter.js physics and an existing particle system in `OrbRenderer`.

## Goals / Non-Goals

**Goals:**
- Fix all 6 identified UX bugs so the onboarding tutorial is completable end-to-end
- Replace the broken spotlight with a working implementation that supports border-radius
- Add visual feedback to the DNA orb when artists are followed (color injection + swirl)
- Add regression tests for the fixed behaviors

**Non-Goals:**
- Redesigning the overall onboarding flow or step sequence
- Adding new onboarding steps
- Changing the backend or proto definitions
- Performance optimization of the Canvas rendering pipeline

## Decisions

### D1: Spotlight — CSS Anchor Positioning Hybrid (box-shadow + transparent click-blockers)

**Chosen**: A `.visual-spotlight` element positioned with `anchor()` functions uses `box-shadow: 0 0 0 100vmax` to create the dark overlay with a transparent cutout. Four invisible `.click-blocker` divs (top/right/bottom/left) also positioned with `anchor()` block clicks outside the target. The spotlight element uses `border-radius: var(--spotlight-radius)` for shape control.

**Alternatives considered**:
- **SVG mask on overlay**: Baseline 2015 support, perfect border-radius via `rx`/`ry`. But requires JS `getBoundingClientRect()` to update SVG rect attributes and `-webkit-mask` prefix. Since the project already depends on CSS Anchor Positioning (used in existing coach-mark tooltip), the browser support advantage is moot.
- **Current approach (child box-shadow inside overlay div)**: Fundamentally broken — parent `background` paints over child's shadow hole. Not fixable without removing the parent background, which defeats the purpose.
- **4-mask only (no visual spotlight)**: Works for click blocking but produces rectangular-only cutouts with no border-radius support.

**Rationale**: The hybrid approach eliminates all JS coordinate calculations (`getBoundingClientRect`, `updateSpotlightPosition`), delegates positioning entirely to the CSS engine, supports arbitrary border-radius via CSS variable, and integrates with View Transitions API for smooth spotlight movement across all target changes — both same-page (lane introduction sequence) and cross-route (Discovery → Dashboard → My Artists). The visual/logic layer separation is clean and testable.

**Implementation pattern** (CSS):

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

.visual-spotlight {
  position: fixed;
  top: anchor(--coach-target top);
  right: anchor(--coach-target right);
  bottom: anchor(--coach-target bottom);
  left: anchor(--coach-target left);
  margin: -8px;
  border-radius: var(--spotlight-radius, 12px);
  box-shadow: 0 0 0 100vmax color-mix(in oklch, oklch(0% 0 0) 70%, transparent);
  pointer-events: none;
  view-transition-name: spotlight;
}

.click-blocker {
  position: fixed;
  background-color: transparent;
  pointer-events: auto;
}
.mask-top    { inset: 0 0 auto 0; bottom: anchor(--coach-target top); }
.mask-bottom { inset: auto 0 0 0; top: anchor(--coach-target bottom); }
.mask-left   { top: anchor(--coach-target top); bottom: anchor(--coach-target bottom); left: 0; right: anchor(--coach-target left); }
.mask-right  { top: anchor(--coach-target top); bottom: anchor(--coach-target bottom); right: 0; left: anchor(--coach-target right); }
```

**Implementation pattern** (JS — anchor-name reassignment wrapped in View Transition):

```typescript
// Target change: wrap in View Transition for smooth spotlight slide
document.startViewTransition(() => {
  this.currentTarget?.style.removeProperty('anchor-name');
  newTarget.style.anchorName = '--coach-target';
  this.currentTarget = newTarget;
});
```

### D2: DNA Orb Color Injection — Bubble Hue Pass-Through

**Chosen**: When the absorption animation delivers a bubble to the orb center, pass the bubble's existing hue (already computed from `artistHue(name)` for canvas rendering) to `OrbRenderer.injectColor(hue)`. This method replaces 5-8 existing particles with new particles at the given hue and triggers a swirl animation (3x rotation speed, ~1000ms decay).

**Rationale**: The bubble already has a deterministic hue computed for rendering. Passing it through the absorption callback avoids re-importing `color-generator.ts` and keeps the data flow unidirectional: bubble → absorption → orb. Over successive follows, the orb accumulates diverse hues, visually representing the user's "Music DNA."

### D3: AuthHook — Onboarding-Aware Fallback

**Chosen**: Insert a new Priority 2.5 check between the current tutorial step check and the "not authenticated" fallback:

```
Priority 2: tutorialStep defined + isOnboarding → allow if step reached
Priority 2.5 (NEW): tutorialStep undefined + isOnboarding → redirect to current step route (no toast)
Priority 3: Not authenticated → toast + redirect to LP
```

**Rationale**: Minimal change. One `if` branch addition. No toast, no user confusion. The redirect takes the user back to wherever they should be in the tutorial.

### D4: Home Nav Click — Step Advancement via Coach Mark

**Chosen**: The existing coach mark targets `[data-nav-dashboard]`. Fix the spotlight (D1) so users can see and tap it. The existing `onCoachMarkTap()` already advances the step and navigates. Additionally, handle the case where a user clicks the nav button directly (bypassing the coach mark overlay) by checking onboarding state in the nav-bar component and advancing the step if the follow threshold is met.

### D5: Progress Bar Removal

**Chosen**: Remove the `search-progress-bar` HTML, CSS, and the `searchProgress` / `completedSearchCount` / `concertSearchStatus` tracking from `DiscoverPage`. The coach mark appearance (triggered when `followedCount >= 3 && completedSearchCount >= followedCount`) remains as the progression signal, but the visual progress indicator is replaced by the DNA orb color evolution.

Note: `completedSearchCount` is still needed for the `showDashboardCoachMark` computed property. Only the progress bar UI and `searchProgress` getter are removed.

### D7: Continuous Spotlight — App-Shell Level Coach Mark

**Chosen**: Move the `<coach-mark>` component from individual route page templates (discover-page, dashboard, my-artists-page) to a single instance in the app shell (`my-app.html`). The onboarding service drives the target selector, message, spotlight radius, and active state. The popover opens once at Step 1 (Dashboard icon) and stays open through Step 5 (Passion Level), with only the target changing via anchor-name reassignment + View Transitions. The popover closes at Step 6 (SignUp modal).

**Alternatives considered**:
- **Per-page coach mark instances (current)**: Each route template creates/destroys its own `<coach-mark>`. This causes the spotlight to blink off and on between steps, breaking the guided flow feel. Also duplicates state management across 3 pages.

**Rationale**: A single app-shell instance naturally supports continuous spotlight across route navigations. View Transitions animate the spotlight slide because the same DOM element persists. The onboarding service already tracks `currentStep` — it simply publishes the target config, and the coach mark reacts. Individual pages become simpler (no coach mark bindings). Cleanup is centralized: one `hidePopover()` call at Step 6.

### D8: Tooltip Arrow — Inline SVG with Drawing Animation

**Chosen**: Add inline SVG arrows to the coach mark tooltip. The arrow is a `<svg>` element with a curved `<path>` for the line and a separate `<path>` for the arrowhead. Direction (up/down) is selected via Aurelia `switch.bind` on the tooltip's resolved `position-area`. The drawing animation uses CSS `stroke-dasharray` / `stroke-dashoffset` (600ms ease-out), and the arrowhead fades in after a 300ms delay.

**Alternatives considered**:
- **External image assets**: Requires HTTP requests, doesn't adapt to theme/color changes, resolution-dependent. Not acceptable for 2026 baseline.
- **CSS-only triangle (`border` trick)**: No curved path, no animation, looks generic.
- **Canvas-drawn arrow**: Overkill, not DOM-inspectable, breaks accessibility.

**Rationale**: Inline SVG with `currentColor` inherits the tooltip's color via CSS cascade — zero theme coupling. The `stroke-dasharray` animation creates an organic "hand-drawn" feel that makes the coach mark feel personal rather than generic UI chrome. Aurelia's `switch.bind` selects the correct arrow direction at compile time with no runtime overhead.

**Implementation pattern** (HTML):

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

**Implementation pattern** (CSS):

```css
.coach-arrow svg {
  width: 80px; height: 80px;
  stroke-width: 4px; stroke-linecap: round; stroke-linejoin: round;
  filter: drop-shadow(0 4px 6px color-mix(in oklch, oklch(0% 0 0) 50%, transparent));
  transform: rotate(-5deg);
}
.arrow-line {
  stroke-dasharray: 150; stroke-dashoffset: 150;
  animation: draw-line 0.6s cubic-bezier(0.25, 1, 0.5, 1) forwards;
}
.arrow-head {
  opacity: 0;
  animation: fade-in-head 0.3s ease-out 0.5s forwards;
}
@keyframes draw-line { to { stroke-dashoffset: 0; } }
@keyframes fade-in-head { to { opacity: 1; } }
@media (prefers-reduced-motion: reduce) {
  .arrow-line { animation: none; stroke-dashoffset: 0; }
  .arrow-head { animation: none; opacity: 1; }
}
```

### D9: Tooltip Handwritten Font

**Chosen**: Use a handwritten-style Google Font (e.g., `Caveat`, `Klee One`, or `Zen Kurenaido` for Japanese text) for the coach mark tooltip message text. The font is loaded via `@import` or `<link>` from Google Fonts and applied to the tooltip message element via `font-family`.

**Rationale**: The handwritten font reinforces the personal, friendly tone of the onboarding guidance — consistent with the hand-drawn SVG arrow (D8) and the organic DNA orb animation (D2). It visually distinguishes coach mark messages from standard UI text, making them feel like personal notes rather than system prompts. Japanese-compatible handwritten fonts (`Klee One`, `Zen Kurenaido`) ensure the Japanese tooltip messages render with the intended aesthetic.

**Implementation pattern** (CSS):

```css
/* Google Fonts import (in global stylesheet or component) */
@import url('https://fonts.googleapis.com/css2?family=Klee+One&display=swap');

.coach-tooltip-message {
  font-family: 'Klee One', cursive;
  font-size: 18px;
  line-height: 1.6;
}
```

### D6: Toast Popover UA Style Reset

**Chosen**: Add explicit popover reset styles to the toast container: `background: transparent; border: none; padding: 0; margin: 0;`. This neutralizes the browser's default popover UA stylesheet which adds white background and border.

## Implementation References

The following research documents contain full implementation examples (Aurelia 2 components, CSS, and JS) that informed the design decisions above. Read these before implementing D1, D7, and D8:

- `docs/research/spotlight-anchor-positioning.md` — CSS Anchor Positioning hybrid spotlight: box-shadow visual layer, transparent click-blockers, Popover API, View Transitions API (D1, D7)
- `docs/research/coach-mark-svg-arrow.md` — Inline SVG directional arrow with `stroke-dasharray` drawing animation, Aurelia `switch.bind` for direction, `currentColor` theming (D8)

## Risks / Trade-offs

- **[Transparent click-blocker corner gap]** → The 4 rectangular blockers leave tiny triangular gaps at rounded corners where clicks can pass through. Mitigation: The gaps are ~3px at 12px border-radius — negligible for finger taps on mobile. Acceptable trade-off for pure-CSS positioning.
- **[anchor() in inset properties]** → While CSS Anchor Positioning is Baseline 2025, using `anchor()` within `inset` shorthand may have edge cases in early implementations. Mitigation: Use longhand properties (`top`, `right`, `bottom`, `left`) if shorthand causes issues. Test on iOS Safari 18+ and Chrome Android.
- **[Orb particle count growth]** → Injecting 5-8 particles per follow could exceed `maxParticles` (60) after many follows. Mitigation: `injectColor()` replaces existing particles rather than adding new ones, keeping the count constant.
- **[Concert search still runs in background]** → Removing the progress bar doesn't remove the background concert search. The search still runs and is needed for `showDashboardCoachMark`. Only the visual indicator is removed.
