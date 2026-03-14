## Why

After establishing the CUBE CSS architecture (`improve-css-design`), significant TS/CSS responsibility leaks remain. TypeScript controls visual state through inline `style=` bindings, class-name ternaries, `setTimeout` with hardcoded animation durations, and string interpolation in `data-*` attributes — all of which violate the three-layer separation principle where TS declares state, templates pass through, and CSS owns visual expression.

The codebase audit found **45 instances** across 15 components:
- 11 class ternary patterns (visual state via CSS class toggling)
- 6 inline style interpolations leaking CSS property names into HTML
- 7 static inline styles that belong in CSS files
- 4 `data-*` attributes using string interpolation instead of `.bind`
- 10 ternary expressions inside `data-*.bind` (violating direct passthrough principle)
- 5 `setTimeout` calls duplicating CSS animation durations
- 2 unnecessary `if.bind` for visual state

These create fragile timing dependencies between TS and CSS, duplicate duration constants, template-level ternary transformations that obscure state flow, and make it impossible to restyle components without modifying TypeScript.

## What Changes

- **Three-layer responsibility separation**: TS ViewModel declares state as enum/boolean/value → Template binds directly via `data-*.bind` and custom attributes (zero transformation, zero ternaries) → CSS owns all visual expression via attribute selectors and custom properties
- **Total `style` attribute ban**: All `style=`, `style.*.bind`, and style interpolation removed from templates. Enforced by grep-based lint rules in `make check`
- **Custom attributes as JS→CSS bridge**: Replace inline style bindings with custom attributes (e.g., `swipe-offset.bind`, `tile-color.bind`) that internally call `element.style.setProperty('--_*')`. Templates never contain `style`. Bridge pattern until CSS `attr()` with `type()` reaches Baseline (est. 2027-2028)
- **Static inline styles → CSS files**: Move `style="font-size: clamp(...)"`, `style="margin-inline: auto"` etc. to component block CSS
- **Class ternaries → `data-*.bind`**: Replace `class="${flag ? 'active' : ''}"` with `data-active.bind="isActive"` + CSS `[data-active="true"]`. Use parent container strategy when multiple children react to the same flag
- **data-* interpolation → `.bind`**: Replace `data-state="${expr}"` with `data-state.bind="state"` — ViewModel exposes enum, template passes through
- **setTimeout → CSS event-driven**: Replace `setTimeout(() => hide(), EXIT_ANIMATION_MS)` with `animationend`/`transitionend` event listeners
- **if.bind for visual state → Popover API / CSS**: Remove `if.bind` on elements where Popover API or CSS transitions manage visibility

## Capabilities

### New Capabilities

- `css-state-management`: Defines the three-layer contract (TS → Template → CSS) for visual state communication — `data-*.bind` for discrete states, custom attributes for continuous values (JS→CSS custom property bridge), CSS events for animation lifecycle, total `style` ban in templates, zero ternaries

### Modified Capabilities

- `cube-css-architecture`: Strengthen exception layer — class toggling for visual state SHALL be prohibited; `data-*` attributes with direct `.bind` (no interpolation) SHALL be the only mechanism; parent container strategy for shared state flags
- `modern-css-platform`: Total `style` attribute ban in templates; custom attributes as JS→CSS bridge; `color-mix()` for dynamic alpha; `translate` shorthand for transforms; grep-based lint enforcement

## Impact

- **frontend**: All component `.ts`, `.html`, and `.css` files that use inline styles, class ternaries, data-* interpolation, ternary-in-bind, or setTimeout for animation. Major refactors in: `my-artists-page`, `event-detail-sheet`, `celebration-overlay`, `loading-sequence`, `pwa-install-prompt`, `notification-prompt`, `discover-page`, `coach-mark`, `toast-notification`, `event-card`, `tickets-page`, `hype-inline-slider`, `dashboard`, `settings-page`, `bottom-nav-bar`
- **specification**: New `css-state-management` spec, delta specs for `cube-css-architecture` and `modern-css-platform`
