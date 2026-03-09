## Layout Architecture: Before and After

### Before (broken)

```
<div>  grid-rows: [1fr min-content], h-dvh
  <main>  grid-rows: [auto auto 1fr], overflow-hidden
    <pwa-install-prompt>       ← row 1 (auto, 0px when hidden)
    <notification-prompt>      ← row 2 (auto) — REMOVED by if.bind!
    <au-viewport>              ← row 2 when prompt absent (auto=177px)
       <discover-page>            display: inline ← blocks height: 100%
         .container                height: 100% → 177px
           .bubble-area            flex: 1 → 0px 🔥
  <bottom-nav-bar>             ← min-content

Problem: au-viewport gets auto (content-sized), 1fr row is empty
```

### After (fixed)

```
<div>  grid-rows: [1fr min-content], h-dvh
  <main>  display: block, overflow-y: auto, height: inherited from 1fr
    <au-viewport>              ← only child, block, height: 100%
       <discover-page>            :host { display: block; height: 100% }
         .container                height: 100% → full available height
           .bubble-area            flex: 1 → fills remaining space ✅
  <bottom-nav-bar>             ← min-content

  <!-- top-layer elements (DOM position irrelevant) -->
  <pwa-install-prompt popover="manual">     ← fixed, top banner
  <notification-prompt popover="manual">    ← fixed, top banner
  <error-banner>                            ← dialog (unchanged)
```

## Design Decisions

### D1: Banners as popover="manual", not popover="auto"

Rationale: `popover="auto"` provides light-dismiss (close on outside click/ESC). Promotional banners should only close when the user explicitly taps the dismiss button or the auto-hide timer fires. `popover="manual"` gives full programmatic control, matching the existing `ToastNotification` pattern.

### D2: Remove nested Grid from `<main>`

Rationale: With banners removed from `<main>`, there is only one child (`<au-viewport>`). A Grid with a single child is unnecessary. A block container with `overflow-y: auto` is simpler and achieves the same layout. The outer `<div>` Grid (`1fr / min-content`) already provides the definite height.

### D3: `au-viewport` height propagation via CSS

```css
au-viewport {
  display: block;
  height: 100%;
  overflow-y: auto;
}
```

This ensures the Aurelia router viewport fills the `<main>` container. `overflow-y: auto` enables per-page scrolling within the viewport area.

### D4: `:host` on discover-page (and all route components)

Each route component that needs full-height layout must set `:host { display: block; height: 100%; }`. This is because Aurelia 2 custom elements default to `display: inline`, which breaks percentage height propagation.

Rather than adding this to every route, we add it only to `discover-page` since it's the only route with a canvas that requires an explicit pixel height. Other routes scroll naturally and don't depend on a definite container height.

### D5: Undo toast as popover="manual"

The undo toast in MyArtistsPage currently uses `position: absolute` within the page's containing block. This works until a `<dialog>` (passion selector or context menu) opens — the dialog's `::backdrop` covers the undo toast, making the undo button unreachable.

Converting to `popover="manual"` promotes it to the top layer, ensuring it's always accessible. This matches the existing `ToastNotification` pattern. The undo toast uses `if.bind` for DOM lifecycle; we switch to persistent DOM + `showPopover()` / `hidePopover()` calls.

### D6: Banner positioning

Both banners use `position: fixed` within the popover to anchor to the viewport top:

```css
[popover] {
  position: fixed;
  inset-block-start: 0;
  inset-inline: 1rem;
  margin: 0;  /* override UA popover centering */
}
```

The `margin: 0` override is necessary because the UA stylesheet for `[popover]` sets `margin: auto` which centers the element. We want top-anchored banners.

## Height Propagation Chain (after fix)

```
<div>              height: 100dvh (explicit)
  ↓ grid-rows: 1fr min-content
<main>             height: from 1fr track (definite)
  ↓ block layout
au-viewport        height: 100% → resolves to main's height
  ↓ block layout
<discover-page>    :host { display: block; height: 100% }
  ↓ shadow DOM
.container         height: 100% → full route height
  ↓ flex column
.bubble-area       flex: 1 → fills remaining space after search + chips
  ↓
<dna-orb-canvas>   :host { display: block; height: 100% }
  ↓ shadow DOM
<canvas>           resize() reads getBoundingClientRect() → valid size ✅
```
