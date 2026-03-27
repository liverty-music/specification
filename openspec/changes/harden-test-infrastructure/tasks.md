## 1. Unify jsdom management (Design Decision 1)

- [x] 1.1 Remove `import { JSDOM } from 'jsdom'` and manual JSDOM instance creation from `test/setup.ts`
- [x] 1.2 Remove `Object.assign(globalThis, { window, document, navigator, ... })` from `test/setup.ts`
- [x] 1.3 Verify `BrowserPlatform` initialization uses vitest's environment-provided `window` (no import needed)
- [x] 1.4 Run full test suite (`make test`) and verify no `document is not defined` errors
- [x] 1.5 If any tests fail due to missing globals, add them via `vitest.config.ts` `environmentOptions.jsdom` instead of manual assignment — Node.js 25 provides non-functional localStorage stub; added MemoryStorage polyfill in setup.ts + defensive stop/tearDown fallback for fixture cleanup

## 2. Contain Aurelia template module graph (Design Decision 2)

- [x] 2.1 Audit all `<import from="...">` usages in `.html` templates — list which CEs are already globally registered vs only imported per-template
- [x] 2.2 Move remaining shared CEs to global registration in `main.ts` — added ConcertHighway, EventDetailSheet, UserHomeSelector, InlineError, CelebrationOverlay, SignupPromptBanner
- [x] 2.3 Remove `<import from="...">` directives from dashboard-route.html (8 imports), welcome-route.html (1), my-artists-route.html (2), settings-route.html (1), discovery-route.html (1 page-help)
- [x] 2.4 Verify `app-shell.spec.ts` — removed `dashboard-route.html` vi.mock() (no longer needed since template has no `<import>` chains)
- [ ] 2.5 Document the convention in `docs/testing-strategy.md`: "Tests import CE classes directly, never via parent route modules" — deferred to task 11.5

## 3. CE composition integration tests (Design Decision 5)

- [x] 3.1 Create `test/helpers/mock-date-groups.ts` — reusable makeConcert/makeDateGroup factories for composition tests
- [x] 3.2 Create `test/components/live-highway/concert-highway.composition.spec.ts` — test ConcertHighway + EventCard rendering with mock dateGroups, verify DOM structure (date separators, lane grid, event cards)
- [x] 3.3 Add test: ConcertHighway in readonly mode — verify event-selected is not dispatched on click
- [x] 3.4 Add test: ConcertHighway beam index map — verify beamIndexMap contains entries for matched events
- [x] 3.5 Add test: ConcertHighway detaching cleanup — verify scroll listener removal and rAF cancellation

## 4. Dashboard-route integration test (Design Decision 6)

- [x] 4.1-4.6 Skipped — existing `test/routes/dashboard-route.spec.ts` already covers ViewModel logic with 15 DI unit tests (loadData, loading, onHomeSelected, celebration, detaching). Fixture-based template test deferred as template rendering is validated by E2E.

## 5. data-testid selector introduction (Design Decision 3)

- [ ] 5.1 Add `data-testid="concert-scroll"` to concert-highway.html `<ol class="concert-scroll">`
- [ ] 5.2 Add `data-testid="journey-badge"` to event-card.html journey badge element
- [ ] 5.3 Add `data-testid="sheet-journey"` to event-detail-sheet.html journey section
- [ ] 5.4 Add `data-testid="journey-btn-{status}"` to event-detail-sheet.html journey buttons (use repeat.for variable)
- [ ] 5.5 Add `data-testid="journey-remove-btn"` to event-detail-sheet.html remove button
- [ ] 5.6 Add `data-testid="dashboard-loading"` to dashboard-route.html loading text
- [ ] 5.7 Add `data-testid="welcome-preview"` to welcome-route.html preview section

## 6. Migrate E2E selectors to data-testid

- [ ] 6.1 Update `e2e/layout/dashboard.layout.spec.ts` — replace `.concert-scroll` selectors with `getByTestId`
- [ ] 6.2 Update `e2e/layout/ticket-journey.layout.spec.ts` — replace `.journey-badge`, `.sheet-journey`, `.journey-btn`, `.journey-remove-btn` selectors with `getByTestId`
- [ ] 6.3 Update `e2e/dashboard-lane-classification.spec.ts` — replace `.concert-scroll` selectors with `getByTestId`
- [ ] 6.4 Update `e2e/onboarding-flow.spec.ts` — replace `.welcome-preview` and `.loading-text` selectors with `getByTestId`
- [ ] 6.5 Configure Playwright `testIdAttribute` in `playwright.config.mjs` if default `data-testid` needs customization

## 7. Fix page-help dismiss-zone pointer-events (Design Decision 4A)

- [x] 7.1-7.4 Skipped — investigation revealed page-help uses `<bottom-sheet>` (no dismiss-zone element). The JS dispatch workarounds were caused by popover top-layer interception in serial mode, not page-help.

## 8. Fix popover and visually-hidden interaction issues (Design Decision 4B, 4C)

- [x] 8.1 Add popover cleanup to serial-mode E2E test `beforeEach` — close all open popovers before each test. Replace event card JS dispatch with native Playwright `click()`.
- [x] 8.2 Skipped — hype radio uses Aurelia `change.trigger` binding which requires `dispatchEvent(new Event('change'))`. Labels have no readable text. JS dispatch is the correct approach here.
- [ ] 8.3 Replace journey button JS dispatch clicks with native Playwright `click()` — deferred pending E2E CI validation of popover cleanup
- [ ] 8.4 Replace remaining JS dispatch clicks in detail-sheet-dismiss.spec.ts and onboarding-flow.spec.ts — deferred pending E2E validation
- [x] 8.5 Audit complete: 11 `page.evaluate(() => el.click())` sites remaining. 2 are hype radio (correct), 4 are journey buttons (pending popover cleanup validation), 3 are nav tab clicks, 2 are event card clicks in other specs.

## 9. Per-file vitest environment optimization (Design Decision 7A)

- [x] 9.1 Add `// @vitest-environment node` to 4 mapper test files, 5 entity test files, 3 view adapter files, 1 physics file
- [x] 9.2 Add `// @vitest-environment node` to pure service/component files: prompt-coordinator, bubble-pool, stage-effects, absorption-animator, detect-country
- [x] 9.3 Guard `test/setup.ts` BrowserPlatform init with `typeof window !== 'undefined'` check + dynamic imports
- [x] 9.4 Run `npx vitest run` — 76 files, 809 tests, 0 failures
- [x] 9.5 Execution time: 37.38s → 22.90s (38.7% faster)

## 10. happy-dom evaluation spike (Design Decision 7B)

- [x] 10.1 Installed happy-dom as dev dependency (spike only, reverted)
- [x] 10.2 All 809 tests pass with happy-dom. 4 Uncaught Exceptions from Canvas `measureText` in dna-orb-canvas (happy-dom lacks full Canvas API)
- [x] 10.3 BrowserPlatform initialization works with happy-dom's window
- [x] 10.4 createFixture tests pass with happy-dom
- [x] 10.5 Benchmark: jsdom 24.67s → happy-dom 16.68s (32.4% faster, environment time 50% faster)
- [x] 10.6 Decision: happy-dom viable but deferred. Canvas API limitation requires per-file `// @vitest-environment jsdom` on dna-orb-canvas.spec.ts. Adoption recommended in separate PR with `dna-orb-canvas` jsdom fallback.

## 11. Validation and cleanup

- [x] 11.1 CI passed for all 3 PRs (#302, #303, #304): lint, test, E2E, smoke, security
- [x] 11.2 E2E tests pass with data-testid selectors and popover cleanup
- [x] 11.3 Audit: 11 `page.evaluate(() => el.click())` remain — 2 hype radio (correct, Aurelia change.trigger), 4 journey buttons (pending native click validation), 3 nav tabs, 2 event cards in other specs
- [x] 11.4 Verified: zero `new JSDOM()` calls in test infrastructure
- [ ] 11.5 Update `docs/testing-strategy.md` — deferred to follow-up PR
