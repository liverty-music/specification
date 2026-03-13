## Why

After establishing the CUBE CSS architecture (`improve-css-design`), significant TS/CSS responsibility leaks remain. TypeScript controls visual state through inline `style=` bindings, class-name ternaries, and `setTimeout` with hardcoded animation durations — all of which should be CSS's responsibility. The CUBE CSS exception layer (`data-*` attributes) and modern CSS features (`animationend`, CSS custom properties) provide the right primitives, but they are underutilized. This creates fragile timing dependencies between TS and CSS, duplicate duration constants, and makes it impossible to restyle components without modifying TypeScript.

## What Changes

- **Inline style= → CSS custom properties**: Replace `style="transform: translateX(${offset}px)"` patterns with `style="--offset: ${offset}px"` and CSS `transform: translateX(var(--offset, 0px))`
- **Class ternaries → data-* exception attributes**: Replace `class="${flag ? 'active' : ''}"` with `data-state="${flag ? 'active' : 'inactive'}"` and CSS `[data-state="active"] { }`
- **setTimeout animation → CSS event-driven**: Replace `setTimeout(() => hide(), EXIT_ANIMATION_MS)` with `animationend`/`transitionend` event listeners — single source of truth for durations in CSS only
- **if.bind for visual state → popover API / hidden**: Remove `if.bind` on elements where the Popover API already manages visibility
- **Aurelia custom attributes**: Create reusable custom attributes for common data-state patterns (e.g., `state-class`, `css-var`)

## Capabilities

### New Capabilities

- `css-state-management`: Defines how visual state SHALL be communicated between TypeScript and CSS — data-* attributes for discrete states, CSS custom properties for continuous values, CSS events for animation lifecycle

### Modified Capabilities

- `cube-css-architecture`: Strengthen exception layer requirements — class toggling for visual state SHALL be prohibited; data-* attributes SHALL be the only mechanism
- `modern-css-platform`: Add requirement for CSS custom properties as the bridge between dynamic TS values and CSS — inline style manipulation of layout/visual properties SHALL be prohibited

## Impact

- **frontend**: All component `.ts`, `.html`, and `.css` files that use inline styles, class ternaries, or setTimeout for animation. Major refactors in: `my-artists-page`, `event-detail-sheet`, `celebration-overlay`, `loading-sequence`, `pwa-install-prompt`, `notification-prompt`, `discover-page`, `coach-mark`
- **specification**: New `css-state-management` spec, delta specs for `cube-css-architecture` and `modern-css-platform`
