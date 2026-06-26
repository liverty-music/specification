## Why

The frontend is a touch-first PWA, but tapping a button or tab gives no press feedback. `:hover` styling is rich yet does nothing on touch, the actual touch press state `:active` is missing on most controls, and the reset clears `-webkit-tap-highlight-color`, so the browser's default tap flash is gone too. The net effect is that primary controls — the bottom-nav tabs and the guest dashboard's "Discover" CTA — feel dead and unresponsive on the exact devices the app targets.

## What Changes

- Introduce an app-wide press-feedback baseline so every native `<button>` responds to `:active` without per-component code.
- Add press feedback to the primary tappables the button baseline cannot reach because they are `<a>` elements: the bottom-nav tabs (`.nav-tab`) and the dashboard guest/empty-state primary CTA (`.discover-cta`).
- Add an `:active` cue to settings list rows (`.settings-row`) where a full-width background-deepen reads better than a scale.
- Every press cue honors `prefers-reduced-motion: reduce` with a non-motion fallback.
- Reuse the project's existing press convention (`transform: scale(...)` + a fast `~50ms ease-in` press-in) rather than inventing a new pattern; components that already define `:active` keep their behavior (`@layer block` > `@layer global`).
- No proto, backend, or API change. No **BREAKING** changes.

## Capabilities

### New Capabilities
- `tap-press-feedback`: The cross-cutting convention that every interactive control gives an immediate, touch-visible press response on `:active`, with a global `<button>` baseline, explicit coverage for non-`<button>` tappables, and a reduced-motion fallback.

### Modified Capabilities
<!-- None. The change reuses existing design-system tokens (--color-brand-accent, --transition-fast) and the @layer cascade (modern-css-platform / cube-css) without changing their requirements. -->

## Impact

- Frontend only. CSS-only change across four files:
  - `src/styles/global.css` — `:where(button):active` baseline + reduced-motion fallback
  - `src/components/bottom-nav-bar/bottom-nav-bar.css` — `.nav-tab` press feedback
  - `src/styles/utilities.css` — `.discover-cta` press feedback (anchor-based CTA)
  - `src/routes/settings/settings-route.css` — `.settings-row` press feedback
- No new dependencies. The `:active` selectors target only elements that satisfy iOS Safari's activation rule (`cursor: pointer` or `<a href>`), so the press cue fires reliably on touch.
- Ships through the standard frontend release path to prod.
