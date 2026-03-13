## 1. Fix containing block chain

- [x] 1.1 Add `position: relative` to `.bubble-area` in `discover-page.css`
- [x] 1.2 Add `overflow: hidden` to `.bubble-area` to clip overflowing canvas content
- [x] 1.3 Change `container-type` from `inline-size` to `size` on `.bubble-area`

## 2. Stacking context verification

- [x] 2.1 Verify `isolation: isolate` is retained on `.discover-layout` for stacking context

## 3. Migrate state toggling to data-state attributes

- [x] 3.1 Add `data-state.bind="isSearchMode ? 'search' : null"` to `.discover-layout` div in `discover-page.html`
- [x] 3.2 Remove `${isSearchMode ? 'hidden' : ''}` class bindings from `.bubble-area` and `.search-results` in `discover-page.html`
- [x] 3.3 Add CSS selectors `.discover-layout[data-state="search"] .bubble-area { display: none; }` and `.discover-layout:not([data-state="search"]) .search-results { display: none; }` in `discover-page.css`

## 4. Fix orb label positioning

- [x] 4.1 Change `.orb-label` `inset-block-end` from `10rem` to `15cqb` (container query block units)
- [x] 4.2 Verify `.orb-label` uses `translate: -50% 0` instead of `transform: translateX(-50%)` (individual transform properties)

## 5. Verification

- [x] 5.1 Run `make check` in frontend to verify linting and tests pass (lint + unit tests pass; E2E discover tests fail on baseline too — pre-existing auth issue)
- [x] 5.2 Layout verification via E2E tests: D3 (canvas fills bubble-area), D5 (bubble-area within nav), D9 (vertical order), D10 (children contained) confirm bubbles render only within bubble-area
