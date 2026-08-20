## Why

On iOS Safari the app has two touch-interaction defects that make core actions unusable, both stemming from browser-engine differences that Android/Chromium hides:

1. **Help sheet auto-closes ("flash then close").** The shared `<bottom-sheet>` opens and immediately dismisses itself on WebKit. A WebKit Playwright reproduction confirmed the cause: the fallback dismiss heuristics (`onScrollEnd` when `scrollRatio < 0.1`, `onPointerUp` when `scrollTop/max < 0.25`) fire on the *programmatic* initial re-snap (measured scroll-ratio trace `[1, 0]`) and misread it as a user swipe-to-dismiss. Because `page-help` auto-opens on first visit, iOS users effectively cannot see help.
2. **Long-press unfollow does not work.** The list-view unfollow is a hidden 500 ms long-press that the iOS system gesture (text selection / callout / magnifier) cancels via `pointercancel` before the timer fires. On touch devices the visible trash column is hidden (`@media (pointer: coarse)`), so long-press is the *only* unfollow path — leaving iOS users unable to unfollow at all.

Both are fixed by aligning with current web-standard best practice: use the purpose-built `scrollsnapchange` event (which by spec fires only on user gestures) for sheet dismiss, and replace the hidden long-press gesture with a discoverable, accessible iOS-style Edit mode.

## What Changes

- **BREAKING (interaction): Retire long-press unfollow.** Remove the long-press gesture, the `ArtistUnfollowSheet` confirmation sheet, the `pointer: coarse` trash-column hiding hack, and the long-press help copy. The `long-press-unfollow` capability is retired in full.
- **Add Edit mode unfollow (My Artists list).** A header "Edit" toggle puts the list into edit mode, revealing a per-row remove (−) control. Tapping it unfollows immediately using the existing optimistic-removal + Undo-toast flow. No gesture, no confirmation sheet. This is the single-pointer, discoverable affordance (WCAG 2.5.1; iOS HIG Edit-mode pattern) and avoids the in-row hype-radio tap conflict that sank two prior swipe attempts.
- **Fix bottom-sheet swipe-dismiss detection.** Make `scrollsnapchange` the primary dismiss signal (user-gesture-only by spec; Chrome 129+, Safari 18.2+), remove the fragile `scrollend`/`pointerup` scroll-ratio heuristics that misfire on programmatic re-snap, add an `IntersectionObserver` fallback for engines without `scrollsnapchange` (Firefox), and keep a small "just opened" dismiss guard. This is a net code reduction and improves iOS behaviour for **all** sheets (page-help, event-detail, post-signup, user-home-selector, …).
- **Update My Artists help content** to describe Edit mode instead of the long-press gesture.
- **Add a WebKit regression guard.** A real-WebKit Playwright project (`webkit-repro`) with a Chromium control asserts the help sheet stays open — RED before the fix, GREEN after.

## Capabilities

### New Capabilities

- `edit-mode-unfollow`: An Edit-mode toggle on the My Artists list that reveals per-row remove controls and unfollows with immediate optimistic removal plus Undo, as the single-pointer accessible unfollow affordance for all pointer types.

### Modified Capabilities

- `bottom-sheet-ce`: Swipe-to-dismiss detection changes from scroll-ratio heuristics (`scrollend`/`pointerup`) to the `scrollsnapchange` event with an `IntersectionObserver` fallback and a just-opened dismiss guard, so a programmatic initial re-snap can no longer auto-close the sheet.
- `my-artists`: The page-help gesture-documentation requirement changes from documenting long-press-to-unfollow to documenting Edit mode.
- `long-press-unfollow`: Retired — all requirements REMOVED (the capability no longer exists; its behavior is superseded by `edit-mode-unfollow`).

## Impact

- **Removed code**: `frontend/src/custom-attributes/long-press.ts`; `frontend/src/components/artist-unfollow-sheet/*`; long-press binding + `openUnfollowSheet` wiring in `my-artists-route.{ts,html}`; the `@media (pointer: coarse) { .artist-unfollow-col { display:none } }` rule; `page-help` long-press section + `longPressTip` i18n keys (ja/en); `long-press` registration in `main.ts`.
- **Changed code**: `frontend/src/components/bottom-sheet/bottom-sheet.ts` (dismiss detection); `bottom-sheet.css` if needed; `my-artists-route.{ts,html,css}` (Edit-mode toggle + per-row remove control + `editing` state); `page-help` My Artists help copy + i18n.
- **Tests**: new `e2e/functional/page-help-sheet-webkit.spec.ts` + `webkit-repro` / `chromium-control` projects in `playwright.config.mjs` (regression guard); update/remove long-press unit tests; add Edit-mode tests.
- **No backend / proto / RPC changes.** Frontend-only; unfollow reuses the existing follow-store flow.
- **Ship**: frontend release to production per project convention.
