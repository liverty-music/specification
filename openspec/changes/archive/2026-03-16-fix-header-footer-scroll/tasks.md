## 1. app-shell.css — Remove External CE Styling and Add Areas

- [x] 1.1 Replace `:scope` grid declaration with `grid-template-areas: "viewport" "nav"` and `grid-template-rows: 1fr auto`
- [x] 1.2 Remove `au-viewport { display: grid; grid-template-rows: minmax(0, 1fr); }` rule
- [x] 1.3 Remove `live-highway { display: block; block-size: 100%; }` rule

## 2. Route Component `:scope` Grid Declarations

- [x] 2.1 `dashboard.css`: Add `:scope { display: grid; grid-template-areas: "main"; grid-template-rows: 1fr; block-size: 100%; min-block-size: 0; }` and assign `grid-area: main` to `.dashboard-main`
- [x] 2.2 `my-artists-page.css`: Add `:scope` grid with areas `"header" "main"`, rows `auto 1fr`, `block-size: 100%`, `min-block-size: 0`. Assign `grid-area` to `.page-header` and `main`. Remove orphaned flex properties (`flex: 1`, `flex-shrink: 0`)
- [x] 2.3 `tickets-page.css`: Same pattern — add `:scope` grid, assign `grid-area` to `.page-header` and `main`. Remove orphaned flex properties
- [x] 2.4 `settings-page.css`: Same pattern — add `:scope` grid, assign `grid-area` to `.page-header` and `main`. Remove orphaned flex properties
- [x] 2.5 `discover-page.css`: Investigate layout structure, add `:scope` grid with appropriate `grid-template-areas`. Remove orphaned flex properties

## 3. live-highway — Own Its Display

- [x] 3.1 Add `:scope { display: block; block-size: 100%; min-block-size: 0; }` to `live-highway.css`

## 4. Dashboard Stale-Banner Overlay Conversion

- [x] 4.1 Update stale-banner CSS: change from grid-row to `position: fixed; inset-block-start: 0; inset-inline: 0` with appropriate `z-index`
- [x] 4.2 Verify stale-banner in `dashboard.html` is outside grid flow and does not affect layout

## 5. Verification

- [x] 5.1 Playwright: dashboard — bottom-nav-bar remains visible when scrolling long concert list
- [x] 5.2 Playwright: my-artists — bottom-nav-bar and page-header remain fixed when scrolling artist list
- [x] 5.3 Playwright: tickets — same fixed header/footer verification (covered by mobile-layout project)
- [x] 5.4 Playwright: settings — same fixed header/footer verification (covered by mobile-layout project)
- [x] 5.5 Playwright: dashboard stale-banner overlay renders correctly above content
- [x] 5.6 Run `make check` — lint passes, tests pass (1 pre-existing flaky test in orb-renderer unrelated to CSS changes)
