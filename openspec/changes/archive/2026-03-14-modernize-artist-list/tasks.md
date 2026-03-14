## 1. DOM Restructure — my-artists-page.html

- [x] 1.1 Remove `.artist-list-inner` wrapper; move its padding to `.artist-list`
- [x] 1.2 Merge `.artist-list-item` and `.artist-row` into a single `.artist-row` element (scroll-snap container)
- [x] 1.3 Add `.artist-row-content` inside `.artist-row` as the grid layout element
- [x] 1.4 Wrap indicator + name in `.artist-identity` element inside `.artist-row-content`
- [x] 1.5 Move `<hype-inline-slider>` inside `.artist-row-content`
- [x] 1.6 Replace `.delete-zone` with `.dismiss-end` element after `.artist-row-content`
- [x] 1.7 Remove all touch event bindings (`touchstart`, `touchmove`, `touchend`, `touchcancel`) and inline `transform` style from artist row

## 2. Grid Alignment — my-artists-page.css

- [x] 2.1 Update `.hype-legend` to `grid-template-columns: 2fr repeat(4, 1fr)` with `grid-template-areas: "spacer watch home nearby away"`
- [x] 2.2 Set `.hype-legend-item:first-child` to `grid-column: 2`
- [x] 2.3 Add `.hype-legend` padding-inline to match `.artist-list` padding
- [x] 2.4 Style `.artist-row-content` as `display: grid; grid-template-columns: 2fr repeat(4, 1fr); grid-template-areas: "name watch home nearby away"`
- [x] 2.5 Style `.artist-identity` with `grid-area: name; display: flex; gap; align-items: center; min-inline-size: 0`
- [x] 2.6 Set `hype-inline-slider` to `grid-column: 2 / -1` within `.artist-row-content`

## 3. Scroll-Snap Swipe — my-artists-page.css

- [x] 3.1 Style `.artist-row` as horizontal scroll container: `overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none`
- [x] 3.2 Style `.artist-row-content` with `flex: 0 0 100%; scroll-snap-align: start`
- [x] 3.3 Style `.dismiss-end` with `flex: 0 0 5rem; scroll-snap-align: end` and danger background + trash icon
- [x] 3.4 Remove all old styles: `.artist-list-inner`, `.artist-list-item`, `.delete-zone`, swipe-related `[data-swiping]` selectors

## 4. View Transitions & Dismiss Logic — my-artists-page.ts

- [x] 4.1 Add scroll event handler `checkDismiss()` that checks `scrollLeft > threshold` and triggers unfollow
- [x] 4.2 Wrap unfollow in `document.startViewTransition()` with fallback for unsupported browsers
- [x] 4.3 Set unique `view-transition-name` per `.artist-row` via `--_vt-name` custom property bound to artist ID
- [x] 4.4 Delete `onTouchStart`, `onTouchMove`, `onTouchEnd` methods
- [x] 4.5 Delete `swipeOffset`, `swipedArtistId`, `swipeTarget`, `isSwiping`, `touchStartX`, `touchStartY` properties
- [x] 4.6 Delete `onLongPress`, `clearLongPressTimer`, `longPressTimer`, `LONG_PRESS_MS`

## 5. Verification

- [x] 5.1 Visual check: header emoji centers align with dot centers across all artist rows
- [x] 5.2 Swipe left on artist row → dismiss-end appears, snap triggers unfollow
- [x] 5.3 Partial swipe snaps back to start position
- [x] 5.4 Vertical scrolling is not blocked by horizontal scroll containers
- [x] 5.5 Hype slider dot taps still work (no conflict with horizontal scroll)
- [x] 5.6 Run `make check` in frontend to confirm lint + tests pass
