## Context

The CUBE CSS exception layer prescribes `data-*` attributes for state-driven styling. The `modern-css-platform` spec already requires `data-state` for animation state and `transitionend` for post-animation cleanup. However, the codebase still has significant TS/CSS responsibility leaks identified in the `improve-css-design` audit:

- **11** class ternary patterns in templates (visual state via CSS class toggling)
- **6** inline style interpolations that leak CSS property names into HTML
- **7** static inline styles that belong in CSS files
- **4** `data-*` attributes using string interpolation instead of `.bind`
- **10** ternary expressions inside `data-*.bind` (violating direct passthrough principle)
- **5** setTimeout-based animation orchestrations duplicating CSS durations
- **2** unnecessary `if.bind` for visual state

## Goals / Non-Goals

**Goals:**
- Establish a three-layer responsibility contract: TS declares state (enum/boolean), Template passes through via `data-*.bind` and custom attributes, CSS owns all visual expression
- **Ban all `style` attributes from templates** — zero occurrences of `style=`, `style.`, or `style="` in `.html` files; enforced via grep-based lint rule in `make check`
- Eliminate all ternary expressions from templates — ViewModel exposes values that templates bind directly
- Eliminate all `setTimeout` calls that duplicate CSS animation/transition durations
- Create custom attributes as the JS→CSS custom property bridge (replacing `style.--_*.bind`)
- Ensure animation durations live in CSS only (single source of truth)

**Non-Goals:**
- Changing the visual design of any component
- Adding new animations or transitions
- Refactoring component architecture or state management
- Adding Container Queries, View Transitions, or Scroll-driven Animations (that's `css-modern-patterns`)

## Decisions

### Decision 1: Three-layer responsibility separation

```
  TS ViewModel              Template (HTML)              CSS
  ══════════════            ═══════════════             ════
  Declares state            Passes through              Owns visual expression
  (enum, boolean, value)    (zero transformation)       (all properties, all selectors)
```

| Value type | ViewModel type | Template binding | CSS consumption |
|---|---|---|---|
| Discrete state (multi-value) | `string` literal union | `data-state.bind="state"` | `[data-state="exiting"]` |
| Boolean state (on/off) | `boolean` | `data-active.bind="isActive"` | `[data-active="true"]` |
| Continuous value (offset, color) | `number` / `string` | custom attribute (e.g., `swipe-offset.bind="val"`) | `var(--_offset)` |

**Critical principle: no ternary expressions in templates.** If a ternary appears, it signals that the ViewModel's abstraction is insufficient. The ViewModel SHALL expose values in a form that templates bind directly.

**Alternative (rejected):** `data-active.bind="expr ? '' : null"` (attribute presence/absence pattern). This requires a ternary in every template binding. Instead, bind the boolean directly and use `[data-active="true"]` in CSS. Both `"true"` and `"false"` are set as string attribute values by Aurelia; CSS matches on the value explicitly.

### Decision 2: No custom attribute for state binding — native Aurelia syntax suffices

The codebase already uses `data-*.bind` natively in 7 places (dashboard, settings, my-artists, bottom-nav-bar). Aurelia 2 resolves `data-*` bindings as HTML attributes automatically — no `& attr` binding behavior is needed because `data-*` attributes have no corresponding DOM properties.

The `state-attr` custom attribute proposed in the original design is **removed**. It would re-implement what Aurelia already provides:

```html
<!-- state-attr custom attribute (REJECTED — reimplements framework) -->
<div state-attr="active.bind: isActive; variant.bind: currentVariant">

<!-- Native Aurelia 2 (ADOPTED — zero additional code) -->
<div data-active.bind="isActive" data-variant.bind="currentVariant">
```

The existing `artist-color` custom attribute remains justified because it performs a computation (artist name → hue value), not just a passthrough.

### Decision 3: Parent container strategy for shared state flags

When multiple child elements react to the same state flag, the `data-*` attribute SHALL be placed on the nearest common parent, and CSS descendant selectors SHALL control child visibility/styling.

```html
<!-- WRONG: same flag repeated on each child -->
<div class="genre-chips" data-hidden.bind="isSearchMode">
<div class="bubble-area" data-hidden.bind="isSearchMode">
<div class="search-results" data-hidden.bind="!isSearchMode">

<!-- RIGHT: one attribute on parent, CSS controls children -->
<div class="discover-layout" data-search-mode.bind="isSearchMode">
  <div class="genre-chips">      <!-- CSS: [data-search-mode="true"] .genre-chips { display: none } -->
  <div class="bubble-area">      <!-- CSS: [data-search-mode="true"] .bubble-area { display: none } -->
  <div class="search-results">   <!-- CSS: [data-search-mode="false"] .search-results { display: none } -->
```

This follows CUBE CSS's principle: state originates at the source (parent), CSS cascades the visual effect to descendants.

### Decision 4: Total `style` attribute ban — custom attributes as JS→CSS bridge

**All forms of `style` in templates are prohibited:**

```html
<!-- ALL PROHIBITED -->
style="margin-inline: auto"             <!-- static → move to CSS file -->
style="transform: translateX(${x}px)"   <!-- interpolation → custom attribute -->
style="--_swipe-x: ${offset}px"         <!-- custom property interpolation → custom attribute -->
style.--_swipe-x.bind="offset + 'px'"   <!-- style.*.bind → custom attribute -->
style.background-color.bind="color"     <!-- style.*.bind → custom attribute -->
```

**Custom attributes replace `style.--_*.bind` as the JS→CSS custom property bridge.** Each custom attribute internally calls `element.style.setProperty('--_*', value)` — the DOM `style` attribute is used under the hood, but it never appears in the template.

```html
<!-- Template: zero style attributes -->
<div swipe-offset.bind="offset">
<div drag-offset.bind="dragOffset">
<div tile-color.bind="artist.color">
```

```typescript
// Custom attribute pattern (~15 lines each)
@customAttribute('swipe-offset')
export class SwipeOffsetAttribute {
  @bindable() value = 0
  private readonly el = resolve(INode) as HTMLElement
  bound() { this.apply() }
  valueChanged() { this.apply() }
  detaching() { this.el.style.removeProperty('--_swipe-x') }
  private apply() { this.el.style.setProperty('--_swipe-x', this.value + 'px') }
}
```

This pattern already exists in the codebase (`artist-color` custom attribute). All new custom attributes follow the same structure.

**Lint enforcement:** grep-based checks in `make check` enforce all template rules:

```makefile
lint-no-style:           # Ban all style attributes in templates
	@! grep -rn 'style[.= ]' src/**/*.html || (echo "ERROR: style attributes banned" && exit 1)

lint-no-class-ternary:   # Ban class ternaries — use data-*.bind instead
	@! grep -rn 'class="[^"]*\$${' src/**/*.html || (echo "ERROR: class ternaries banned" && exit 1)

lint-no-data-interpolation:  # Ban data-* interpolation — use .bind
	@! grep -rn 'data-[a-z-]*="[^"]*\$${' src/**/*.html || (echo "ERROR: data-* interpolation banned" && exit 1)

lint-no-bind-ternary:    # Ban ternaries in data-*.bind — ViewModel exposes typed values
	@! grep -rn 'data-[a-z-]*\.bind="[^"]*?[^"]*"' src/**/*.html || (echo "ERROR: ternary in .bind banned" && exit 1)
```

Each rule enforces a specific layer of the three-layer separation:
- `lint-no-style`: CSS owns visual expression (no style leaks into HTML)
- `lint-no-class-ternary`: state via `data-*`, not CSS classes
- `lint-no-data-interpolation`: template passes through via `.bind`, not interpolation
- `lint-no-bind-ternary`: ViewModel exposes typed values, template does zero transformation

**Migration path to CSS `attr()`:** CSS `attr()` with `type()` coercion (CSS Values Level 5) would eliminate the need for custom attributes entirely — `data-offset.bind="42"` + CSS `translate: attr(data-offset px, 0) 0`. However, `type()` is currently Chromium-only (Chrome 133+); Firefox and Safari lack support (est. 2027-2028 Baseline). The custom attribute approach is a bridge: when `attr()` reaches Baseline, custom attributes can be replaced with `data-*.bind` + CSS `attr()` without changing the template API.

### Decision 5: animationend/transitionend for animation lifecycle

Replace `setTimeout(() => cleanup(), DURATION_MS)` with CSS event listeners. Two distinct setTimeout categories exist:

1. **Animation timing duplicates** (e.g., `EXIT_ANIMATION_MS = 600` mirroring CSS `transition-duration`): Replace with `transitionend`/`animationend` listener.
2. **Display duration timers** (e.g., celebration overlay's 2500ms show time): Replace with CSS `animation-delay` + `animationend`, with `prefers-reduced-motion` variant handled via `@media`.

For `prefers-reduced-motion`, detect via `matchMedia('(prefers-reduced-motion: reduce)')` and run cleanup immediately since no transition fires.

**Note:** `celebration-overlay.ts` already implements `transitionend` for fade-out cleanup. The remaining change is replacing the display-duration `setTimeout` with CSS animation delay.

### Decision 6: Remove if.bind where Popover API manages visibility

For `celebration-overlay` and `coach-mark`, remove `if.bind="visible"` and rely on the Popover API's `showPopover()`/`hidePopover()` which manages top-layer visibility natively. CSS handles transitions via `[data-state]`.

### Decision 7: `color-mix()` replaces hex opacity hacks

Dynamic color alpha SHALL use CSS `color-mix()` (2023 Baseline) instead of appending hex alpha suffixes to color strings:

```html
<!-- WRONG: hex alpha hack in template -->
style="background: linear-gradient(135deg, ${color}40, ${color}10)"

<!-- RIGHT: custom attribute + CSS color-mix -->
<div tile-color.bind="artist.color">
```
```css
.grid-tile {
  background: linear-gradient(135deg,
    color-mix(in oklch, var(--_tile-color) 25%, transparent),
    color-mix(in oklch, var(--_tile-color) 6%, transparent)
  );
}
```

### Decision 8: CSS `translate` shorthand replaces `transform: translateX/Y`

Use the `translate` CSS property (2022 Baseline) instead of `transform: translateX()` / `transform: translateY()`:

```css
/* WRONG */
.artist-row { transform: translateX(var(--_swipe-x, 0)); }

/* RIGHT */
.artist-row { translate: var(--_swipe-x, 0) 0; }
```

Benefits: `translate` is independently animatable, works with `will-change: translate`, and doesn't conflict with other transforms.

## Risks / Trade-offs

- [Risk] Custom attributes for CSS custom property bridge add ~5 small files (~15 lines each, ~75 lines total) — Acceptable; they follow the existing `artist-color` pattern and will be replaced by `data-*.bind` + CSS `attr()` when it reaches Baseline.
- [Risk] Gesture-driven custom attributes (swipe, drag) call `element.style.setProperty()` every frame — This is the same DOM operation as `style.--_*.bind`; performance is identical. CSS custom properties on `style=` are the standard pattern for frame-by-frame updates.
- [Risk] `transitionend` may not fire if element is removed before transition completes — Use `{ once: true }` and ensure element remains in DOM during transition (if.bind removal helps here).
- [Risk] `[data-active="true"]` is 3 characters longer than `[data-active]` in CSS selectors — Acceptable cost for eliminating all template ternaries and maintaining a single consistent binding pattern.
- [Risk] Parent container strategy requires CSS to know about child class names — This is already the norm in CUBE CSS block layer; `@scope` can formalize the boundary if needed.
- [Risk] grep-based lint for `style` ban may have false positives in comments or text content — `.html` template files rarely contain prose with the word "style"; if needed, refine the pattern to `style[.="']`.
