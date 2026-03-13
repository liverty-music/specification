## 1. Custom attributes for JS→CSS custom property bridge

- [x] 1.1 Create `src/custom-attributes/swipe-offset.ts` — sets `--_swipe-x` on host element. Replace `my-artists-page.html` `style="transform: translateX(${offset}px)"` with `swipe-offset.bind="offset"`. CSS: `translate: var(--_swipe-x, 0) 0`
- [x] 1.2 Create `src/custom-attributes/drag-offset.ts` — sets `--_drag-y` on host element. Replace `event-detail-sheet.html` `style="transform: ${dragOffset > 0 ? ...}"` with `drag-offset.bind="dragOffset"`. CSS: `translate: 0 var(--_drag-y, 0)`
- [x] 1.3 Create `src/custom-attributes/tile-color.ts` — sets `--_tile-color` on host element. Replace `my-artists-page.html` `style="background: linear-gradient(135deg, ${color}40, ${color}10)"` with `tile-color.bind="artist.color"`. CSS: `color-mix(in oklch, ...)` gradient
- [x] 1.4 Create `src/custom-attributes/dot-color.ts` — sets `--_dot-color` on host element. Replace `my-artists-page.html` `style="background-color: ${artist.color}"` with `dot-color.bind="artist.color"`. CSS: `background-color: var(--_dot-color)`
- [x] 1.5 Refactor `coach-mark.html`: replace `style="--spotlight-radius: ${spotlightRadius}"` with `spotlight-radius.bind` on existing coach-mark component (internal `style.setProperty`, no template `style=`)
- [x] 1.6 Refactor `hype-inline-slider.html`: replace `style="--artist-color: ${artistColor}"` (L10) — use existing `artist-color` custom attribute or create `hype-color` custom attribute that sets `--_artist-color`
- [x] 1.7 Unit tests for all new custom attributes (verify `--_*` property set/removed on bind/unbind)

## 2. Static inline styles → CSS files

- [x] 2.1 `event-card.html`: move `style="font-size: clamp(12px, 5cqi, 24px)"` (×3 instances) to `.event-card` block CSS
- [x] 2.2 `notification-prompt.html`: move `style="margin-block-start: 0.75rem"` to block CSS
- [x] 2.3 `tickets-page.html`: move spinner styles (`inline-size`, `block-size`, `border-color`, `border-block-start-color`) to `.spinner` block CSS
- [x] 2.4 `tickets-page.html`: move `style="margin-inline: auto"` and `style="margin-block-start: var(--space-xs)"` to block/utility CSS

## 3. data-* interpolation → `data-*.bind`

- [x] 3.1 `celebration-overlay.html`: replace `data-state="${fadingOut ? 'exiting' : 'active'}"` — change ViewModel to expose `state: 'active' | 'exiting'` enum, bind as `data-state.bind="state"`
- [x] 3.2 `toast-notification.html`: replace `data-severity="${toast.severity}"` with `data-severity.bind="toast.severity"`
- [x] 3.3 `toast-notification.html`: replace `data-state="${toast.visible ? 'entering' : 'exiting'}"` — change ViewModel to expose `toast.state: 'entering' | 'exiting'` enum, bind as `data-state.bind="toast.state"`
- [x] 3.4 `my-artists-page.html`: replace `data-swiping="${expr ? 'true' : 'false'}"` — bind boolean directly as `data-swiping.bind="isSwiping"`, CSS uses `[data-swiping="true"]`

## 4. Class ternary → data-*.bind (parent container strategy)

- [x] 4.1 `discover-page`: add `data-search-mode.bind="isSearchMode"` on `.discover-layout` parent — remove class ternaries from `.genre-chips` (L35), `.bubble-area` (L55), `.search-results` (L74). CSS uses `[data-search-mode="true"] .genre-chips { display: none }` etc.
- [x] 4.2 `discover-page`: genre chip active state — replace `class="genre-chip ${activeTag === tag ? 'active' : ''}"` with `data-active.bind="activeTag === tag"` + CSS `[data-active="true"]`
- [x] 4.3 `discover-page`: follow button — replace `class="follow-button ${isArtistFollowed(artist.id) ? 'followed' : ''}"` with `data-followed.bind="isArtistFollowed(artist.id)"` + CSS `[data-followed="true"]`
- [x] 4.4 `discover-page`: guidance hiding — replace `class="hud-message ${guidanceHiding ? 'hiding' : ''}"` with `data-hiding.bind="guidanceHiding"` + CSS `[data-hiding="true"]`

## 5. Class ternary → data-*.bind (individual element state)

- [x] 5.1 N/A — `hype-btn` with `pulsingArtistId` removed by PR #169 (replaced by hype-inline-slider)
- [x] 5.2 `loading-sequence.html`: phase class — replace `class="loading-message ${getPhaseClass()}"` with `data-phase.bind="currentPhase"` + CSS `[data-phase="intro"]`, `[data-phase="progress"]` etc.
- [x] 5.3 `loading-sequence.html`: step dot class — replace `class="step-dot ${getStepDotClass(i)}"` with `data-step-state.bind="getStepState(i)"` + CSS `[data-step-state="complete"]`, `[data-step-state="active"]` etc.
- [x] 5.4 `notification-prompt.html`: animation class — replace `class="prompt-popover ${animationClass}"` with `data-animation.bind="animationState"` + CSS `[data-animation="fade-slide-up"]`
- [x] 5.5 `pwa-install-prompt.html`: animation class — same pattern as 5.4
- [x] 5.6 `event-card.html`: hype level class — replace `class="event-card hype-${event.hypeLevel}"` (×3 variants) with `data-hype.bind="event.hypeLevel"` + CSS `[data-hype="obsessed"]` etc.

## 6. Ternary in `data-*.bind` → direct passthrough

- [x] 6.1 `discover-page.html` L6: replace `data-state.bind="isSearchMode ? 'search' : null"` — change to `data-search-mode.bind="isSearchMode"` (boolean), CSS uses `[data-search-mode="true"]` descendant selectors (aligns with parent container strategy, task 4.1)
- [x] 6.2 `dashboard.html` L21: replace `data-blurred.bind="needsRegion ? '' : null"` with `data-blurred.bind="needsRegion"` + CSS `[data-blurred="true"]`
- [x] 6.3 `settings-page.html` L68: replace `data-disabled.bind="!vapidAvailable ? '' : null"` with `data-disabled.bind="!vapidAvailable"` + CSS `[data-disabled="true"]`
- [x] 6.4 `settings-page.html` L81-82: replace `data-on.bind="notificationsEnabled ? '' : null"` (×2, track + thumb) with `data-on.bind="notificationsEnabled"` + CSS `[data-on="true"]`
- [x] 6.5 `my-artists-page.html` L154: replace `data-active.bind="contextMenuArtist.hype === level ? '' : null"` with `data-active.bind="contextMenuArtist.hype === level"` + CSS `[data-active="true"]`
- [x] 6.6 `hype-inline-slider.html` L8: replace `data-active.bind="stop === hypeLevel ? '' : null"` with `data-active.bind="stop === hypeLevel"` + CSS `[data-active="true"]`
- [x] 6.7 `bottom-nav-bar.html` L6-7: replace `data-nav-dashboard.bind="tab.icon === 'home' ? '' : null"` and `data-nav-my-artists.bind="..."` — consolidate to `data-nav.bind="tab.icon"` (enum) + CSS `[data-nav="home"]`, `[data-nav="my-artists"]`
- [x] 6.8 `bottom-nav-bar.html` L9: replace `data-active.bind="isActive(tab.path) ? '' : null"` with `data-active.bind="isActive(tab.path)"` + CSS `[data-active="true"]`

## 7. setTimeout → animationend/transitionend

- [x] 7.1 `celebration-overlay.ts`: kept deliberate UX display-duration timer `setTimeout(startFadeOut, 2500)` — not a CSS duration sync
- [x] 7.2 `pwa-install-prompt.ts`: replace `setTimeout(hidePopover, EXIT_ANIMATION_MS)` with `animationend` listener on popover element with `animationend` listener + `prefers-reduced-motion` fallback
- [x] 7.3 `notification-prompt.ts`: same pattern as 7.2
- [x] 7.4 `my-artists-page.ts`: kept deliberate 300ms feedback pulse `setTimeout` — visual UX timing, not CSS duration sync
- [x] 7.5 `loading-sequence.ts`: extract `FADE_DURATION_MS` to CSS-only, use `transitionend` on phase message element for sequencing + `prefers-reduced-motion` fallback
- [x] 7.6 Remove all `EXIT_ANIMATION_MS`, `FADE_DURATION_MS`, and similar TS constants that duplicate CSS durations

## 8. Remove if.bind for visual-only visibility

- [x] 8.1 `celebration-overlay.html`: removed `if.bind="visible"`, visibility via `data-state="hidden"` + CSS `display: none`
- [x] 8.2 `coach-mark.html`: remove `if.bind="visible"`, rely on Popover API `showPopover()`/`hidePopover()` for visibility

## 9. Lint rules: enforce three-layer separation in templates

- [x] 9.1 Add `lint-no-style` target — `grep -rn 'style[.= ]' src/**/*.html` exits non-zero if any match
- [x] 9.2 Add `lint-no-class-ternary` target — `grep -rn 'class="[^"]*\${' src/**/*.html` exits non-zero if any match
- [x] 9.3 Add `lint-no-data-interpolation` target — `grep -rn 'data-[a-z-]*="[^"]*\${' src/**/*.html` exits non-zero if any match
- [x] 9.4 Add `lint-no-bind-ternary` target — `grep -rn 'data-[a-z-]*\.bind="[^"]*?[^"]*"' src/**/*.html` exits non-zero if any match
- [x] 9.5 Add all 4 lint targets to the `check` dependency chain (runs alongside existing lint/test)
- [x] 9.6 Verify zero matches for all 4 rules after all tasks in sections 1-6 are complete

## 10. Attribute binding improvements

- [x] 10.1 `event-card.html`: collapsed 3 `if.bind` blocks into 1 — `data-lane.bind="lane"`, conditional `location-label` via `if.bind="lane !== 'home'"` (54→17 lines)
- [x] 10.2 `hype-inline-slider.html`: replaced `aria-label="${stop}"` with `aria-label.bind="stop"`
- [x] 10.3 `bottom-nav-bar.html`: replaced `href="${tab.path}"` with `href.bind="tab.path"`
- [x] 10.4 `dashboard.html`: changed literal `.bind` to `.one-time` for `loading.one-time="true"`, `loading.one-time="false"` (×3)
- [x] 10.5 `discover-page.html`: changed `show-followed-indicator.bind="true"` to `.one-time`
- [x] 10.6 `discover-page.html`: extracted SR status to ViewModel `srStatusText` getter, bound via `textcontent.bind`
- [x] 10.7 Event-card tests pass without changes (template consolidation preserves same DOM structure per lane)

## 11. Verification

- [x] 11.1 `make lint` passes — zero errors (biome, stylelint, template lint, typecheck)
- [x] 11.2 `make test` passes — 53 files, 528 tests passed
- [x] 11.3 Zero `style` attributes in `.html` files
- [x] 11.4 Zero `class="${...}"` ternary patterns
- [x] 11.5 Zero `data-*="${` interpolation patterns
- [x] 11.6 Zero ternary expressions in `data-*.bind`
- [x] 11.7 Zero `aria-label="${` interpolation patterns
