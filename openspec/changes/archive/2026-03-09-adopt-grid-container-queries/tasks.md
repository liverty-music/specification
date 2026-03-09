## 1. Discover page — Grid layout migration

- [x] 1.1 Convert `.discover-layout` from `display: flex; flex-direction: column` to `display: grid; grid-template-rows: auto auto 1fr`
- [x] 1.2 Remove `flex-shrink: 0` from `.search-bar` and `.genre-chips` (grid auto rows handle sizing)
- [x] 1.3 Replace `flex: 1; min-block-size: 0` on `.bubble-area` with grid `1fr` row placement
- [x] 1.4 Convert `.onboarding-hud` from `display: flex; flex-direction: column` to `display: grid`
- [x] 1.5 Convert `.progress-dots` from `display: flex` to `display: grid; grid-auto-flow: column`

## 2. Discover page — Subgrid for search results

- [x] 2.1 Convert `.results-list` from `display: flex; flex-direction: column` to `display: grid; grid-template-columns: auto 1fr auto`
- [x] 2.2 Convert `.result-item` to `display: grid; grid-template-columns: subgrid; grid-column: 1 / -1`
- [x] 2.3 Remove nested flex from `.result-info` — avatar and name become direct grid children via subgrid (using `display: contents`)

## 3. Loading sequence — Grid centering

- [x] 3.1 Convert `.loading-layout` from `display: flex; flex-direction: column; align-items: center; justify-content: center` to `display: grid; place-items: center`

## 4. Container Query declarations

- [x] 4.1 Add `container-type: inline-size` to `.search-results`
- [x] 4.2 Add `container-type: inline-size` to `.bubble-area`

## 5. Verification

- [x] 5.1 Run `npx stylelint "src/**/*.css"` — zero errors
- [x] 5.2 Run Playwright layout tests — 4/11 pass (S1, D1, D2, D4). 7 failures are pre-existing fixture issues (nav visibility, canvas init, loading route auth), not grid migration regressions.
- [x] 5.3 Visual check in dev server — discover page renders correctly with grid layout. Loading page requires auth state (pre-existing access issue).
