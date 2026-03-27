## 1. Top-layer color inheritance fix (Bug 1)

- [x] 1.1 Add `:where([popover], dialog) { color: var(--color-text-primary); }` to `frontend/src/styles/global.css`
- [x] 1.2 Remove per-component `color: var(--color-text-primary)` overrides that are now redundant (e.g., `user-home-selector.css` `.selector-title`, `.selector-btn`) — reviewed: kept intentional per-element color assignments that contrast with secondary/muted siblings
- [x] 1.3 Verify page-help bottom-sheet text is readable on Discovery, Dashboard, and My Artists pages — deferred to task 5.4

## 2. Eliminate data-stage selector collision (Bug 2-3)

- [x] 2.1 In `page-help.html`, replace `data-stage="home|near|away"` attributes on `<strong>` elements with CSS classes `stage-home`, `stage-near`, `stage-away`
- [x] 2.2 In `page-help.css`, update selectors from `.stage-label[data-stage="home"]` to `.stage-home` (and similarly for near/away)
- [x] 2.3 Scope lane intro spotlight selectors in `dashboard-route.ts` from `'[data-stage="home"]'` to `'concert-highway [data-stage="home"]'` (and near/away)

## 3. Reactive spotlight activation with @watch + queueTask (Bug 2-3-4)

- [x] 3.1 In `dashboard-route.ts`, change `loading()` to `await this.loadDashboardEvents()` when `needsRegion` is false (block until data ready)
- [x] 3.2 In `startLaneIntro()`, remove the `needsRegion` branch's `activateSpotlight()` call — only open `homeSelector` without spotlight
- [x] 3.3 Remove the `while (this.isLoading) await sleep(100)` polling loop from `startLaneIntro()`
- [x] 3.4 Add `@watch((vm: DashboardRoute) => vm.dateGroups.length)` handler that triggers spotlight activation when dateGroups transitions from empty to non-empty
- [x] 3.5 Use `queueTask()` inside the `@watch` handler to defer `updateSpotlightForPhase()` until after Aurelia's DOM update cycle
- [x] 3.6 Update `onHomeSelected()` to not call `updateSpotlightForPhase()` directly — let the `@watch` handler drive it

## 4. Coach-mark invisible target rejection (defense-in-depth)

- [x] 4.1 In `coach-mark.ts` `findAndHighlight()`, after `querySelector` returns an element, check if it's visible (`offsetParent !== null` and `getBoundingClientRect()` has non-zero dimensions)
- [x] 4.2 If the element is invisible, treat it as not found and continue exponential backoff retry

## 5. Verification

- [x] 5.1 Run `make check` in frontend (lint + test)
- [ ] 5.2 Manual E2E test: complete onboarding flow as guest (discovery → dashboard with needsRegion → home selection → lane intro → celebration) — requires deployment
- [ ] 5.3 Manual E2E test: complete onboarding flow as guest with region already set (discovery → dashboard → lane intro → celebration) — requires deployment
- [ ] 5.4 Verify page-help readability on all 3 pages (discovery, dashboard, my-artists) — requires deployment
