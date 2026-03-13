## 1. Inline style= → CSS custom properties

- [ ] 1.1 Refactor `my-artists-page.html` swipe transform: replace `style="transform: translateX(${offset}px)"` with `style="--_swipe-offset: ${offset}px"` and CSS `transform: translateX(var(--_swipe-offset, 0px))`
- [ ] 1.2 Refactor `my-artists-page.html` artist gradient: replace `style="background: linear-gradient(135deg, ${color}40, ${color}10)"` with `style="--_artist-color: ${color}"` and CSS gradient using `var(--_artist-color)`
- [ ] 1.3 Refactor `event-detail-sheet.html` drag transform: replace `style="transform: ${...}"` with `style="--_drag-offset: ${dragOffset}px"` and CSS `transform: translateY(var(--_drag-offset, 0px))`

## 2. Class ternary → data-* exception attributes

- [ ] 2.1 Refactor `discover-page.html` genre chips visibility: replace `class="genre-chips ${isSearchMode ? 'hidden' : ''}"` with `data-search-mode` attribute + CSS selector
- [ ] 2.2 Refactor `discover-page.html` search results visibility: replace `class="search-results ${isSearchMode ? '' : 'hidden'}"` with `data-search-mode` attribute + CSS selector
- [ ] 2.3 Refactor `my-artists-page.html` hype pulse: replace `class="hype-btn ${pulsingArtistId === artist.id ? 'animate-hype-pulse' : ''}"` with `data-pulsing` attribute + CSS selector
- [ ] 2.4 Refactor `discover-page.html` guidance hiding: replace `class="hud-message ${guidanceHiding ? 'hiding' : ''}"` with `data-guidance-state` attribute + CSS selector

## 3. setTimeout → animationend/transitionend

- [ ] 3.1 Refactor `celebration-overlay.ts`: replace `setTimeout(startFadeOut, displayDuration)` → use CSS animation with built-in delay, listen to `animationend` for cleanup
- [ ] 3.2 Refactor `pwa-install-prompt.ts` `hideWithAnimation()`: replace `setTimeout(hidePopover, EXIT_ANIMATION_MS)` → listen to `animationend` on popover element
- [ ] 3.3 Refactor `notification-prompt.ts` `hideWithAnimation()`: same pattern as 3.2
- [ ] 3.4 Refactor `my-artists-page.ts` hype pulse: replace `setTimeout(() => pulsingArtistId = '', 300)` → listen to `animationend` on the button element
- [ ] 3.5 Refactor `loading-sequence.ts` phase transitions: extract `FADE_DURATION_MS` to CSS-only, use `transitionend` on the phase message element for sequencing
- [ ] 3.6 Remove all `EXIT_ANIMATION_MS`, `FADE_DURATION_MS`, and similar TS constants that duplicate CSS durations

## 4. Remove if.bind for visual-only visibility

- [ ] 4.1 Refactor `celebration-overlay.html`: remove `if.bind="visible"`, keep element in DOM, manage visibility via `data-state` + CSS
- [ ] 4.2 Refactor `coach-mark.html`: remove `if.bind="visible"`, rely on Popover API `showPopover()`/`hidePopover()` for visibility

## 5. Aurelia custom attribute for state binding

- [ ] 5.1 Evaluate whether a `state-attr` custom attribute is warranted based on the number of remaining data-* bindings after steps 1-4
- [ ] 5.2 If warranted, create `src/custom-attributes/state-attr.ts` with unit tests

## 6. Verification

- [ ] 6.1 Run `make check` — zero stylelint errors, zero biome errors
- [ ] 6.2 Run `make test` — all unit tests pass
- [ ] 6.3 Grep for remaining `setTimeout` calls that duplicate CSS durations — zero matches
- [ ] 6.4 Grep for remaining `class="${.*?}"` ternary patterns for visual state — zero matches
- [ ] 6.5 Grep for remaining inline `style="transform:` or `style="background:` patterns — zero matches
