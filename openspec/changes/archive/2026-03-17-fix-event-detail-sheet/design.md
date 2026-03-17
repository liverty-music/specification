## Context

The `event-detail-sheet` component uses `<dialog popover="auto">` rendered in the browser's top layer. The CSS is authored inside `@layer block` following the project's CUBE CSS methodology.

The browser's UA stylesheet applies default popover positioning (`inset: 0; margin: auto`) which, due to CSS cascade rules, takes priority over author styles declared inside `@layer`.

The swipe-to-dismiss mechanism uses CSS scroll snap with a content area and a dismiss zone. Scrolling past the content into the dismiss zone triggers close via the `scrollend` event.

### Why the original CSS-only approach failed

The initial plan was to match the `user-home-selector` pattern (higher-specificity selector, explicit `translate`, longhand `inset`). Playwright verification showed this fixed the computed styles but the visual centering bug persisted. Root cause: the dismiss zone (30vh) was visible within the scroll container at rest (70vh `max-block-size`), making the card appear vertically centered. Two alternative approaches were evaluated:

1. **`position: absolute` dismiss zone**: Creates correct popover height, but `scroll-snap-align` on out-of-flow elements is unreliable — the snap engine always snapped to the dismiss zone and never snapped back to `scrollTop: 0`.
2. **Fullscreen Snap Architecture**: Solves both problems. Adopted as the final approach.

## Goals / Non-Goals

**Goals:**
- Sheet card anchors flush to the bottom of the viewport
- Entire sheet surface is draggable for pull-to-dismiss (swipe down)
- Backdrop fades out in real-time during dismiss (both swipe and tap)

**Non-Goals:**
- Changing the visual design or content layout of the card itself
- Adding JS-based height measurement or layout thrashing

## Decisions

### 1. Fullscreen Snap Architecture

The dialog fills the entire viewport. Two 100dvh snap pages give the scroll snap engine unambiguous targets:

```
┌──────────────────────────────────┐
│ Dialog (inset: 0, 100dvh)        │
│ ┌────────────────────────────┐   │
│ │ Page 1: dismiss zone       │   │  scrollTop=0
│ │ (100dvh, transparent)      │   │
│ └────────────────────────────┘   │
│ ┌────────────────────────────┐   │
│ │ Page 2: sheet-page         │   │  scrollTop=100dvh
│ │ (100dvh, flex-end)         │   │
│ │    ┌──────────────────┐    │   │
│ │    │ card (fit-content)│    │   │  pinned to viewport bottom
│ │    └──────────────────┘    │   │
│ └────────────────────────────┘   │
└──────────────────────────────────┘
```

- **On open**: `scrollTop = scrollHeight` (instant, no scrollend fires) scrolls to the card page.
- **Swipe down**: scrolls toward dismiss zone (scrollTop=0). `onScrollEnd` detects `scrollTop < maxScroll` and calls `close()`.
- **Small swipe**: `scroll-snap-stop: always` with `mandatory` snapping returns to card page. No dismiss.

**Why this works**: Both snap points are exactly 100dvh, eliminating the ambiguity that caused the original centering and snap-back bugs.

**Why `flex-end`**: Pins the card to the bottom of the 100dvh page, matching the visual design spec.

### 2. Reversed page order (dismiss zone first)

The dismiss zone is placed **above** the card in DOM order so that swiping **down** (the natural gesture for dismissing a bottom sheet) scrolls toward it.

### 3. Unified dismiss animation via `--_backdrop-opacity`

A CSS custom property `--_backdrop-opacity` is set on the dialog element via `style.setProperty()` during scroll. The `::backdrop` reads it as `opacity: var(--_backdrop-opacity, 1)`.

- `onScroll`: Computes `progress = scrollTop / maxScroll` (1 at card, 0 at dismiss zone) and sets `--_backdrop-opacity`.
- `onBackdropClick`: Instead of calling `close()` directly, triggers `scrollTo({ top: 0, behavior: 'smooth' })` — the same scroll-based dismiss as swipe, giving identical visual feedback.

**Trade-off**: This uses `style.setProperty()` which is technically an inline style. This is acceptable because it's a runtime animation value (like `transform` in a drag), not a layout declaration. No layout thrashing occurs — only compositor-friendly `opacity` changes.

### 4. CSS specificity and UA overrides

Retained from the original plan:
- `dialog.event-detail-sheet` selector (element+class) for higher specificity against UA `[popover]:popover-open`
- `translate: 0 0` to explicitly reset UA positioning
- `display: block` to override dialog's default `display: none`

### 5. Light dismiss behavior with fullscreen popover

With `popover="auto"` and a fullscreen dialog, native click-outside light dismiss cannot fire (all clicks land inside the popover). This is handled by:
- **Backdrop click**: `onBackdropClick()` on the transparent `sheet-page` area, with `stopPropagation()` on the card to prevent card clicks from triggering dismiss.
- **Escape key**: Still works natively via `popover="auto"`.
- **Android back**: Handled by the existing `popstate` listener.

## Risks / Trade-offs

- **`style.setProperty` for backdrop opacity**: Minimal concern — runtime animation value, not a layout property. Documented above.
- **Browser compatibility**: `scroll-snap-stop: always`, `100dvh`, `@starting-style`, `allow-discrete` are 2023-2024 baseline. All target browsers support them.
- **`scrollend` timing**: The scroll snap animation can take 1-2 seconds. The real-time `onScroll` backdrop fade eliminates the perceived delay.
