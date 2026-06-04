## 1. Canonical journey-status presentation map

- [ ] 1.1 Add `JOURNEY_STATUS_CONFIG` (status → labelKey, icon, hueToken) as a plain exported const in `src/entities/ticket-journey.ts`, with icons `tracking`👀 `applied`📝 `unpaid`💰 `paid`🎟️ `lost`💔
- [ ] 1.2 Add a unit test asserting the map covers all five statuses and reuses the existing `eventDetail.journeyStatus.*` i18n keys
- [ ] 1.3 Refactor `event-card` journey badge to source its label/icon/hue from `JOURNEY_STATUS_CONFIG` (no inline per-status values)
- [ ] 1.4 Refactor `event-detail-sheet` journey status control to source label/icon/hue from the map, updating the `lost` glyph to 💔

## 2. Dashboard ViewModel — journey filter and counts

- [ ] 2.1 Add `@observable filteredStatuses: JourneyStatus[]` to `DashboardRoute` and parse the `journey` query param in `loading()`; ignore the param entirely for unauthenticated users (guests get the unfiltered view — the param has no effect, never an empty highway)
- [ ] 2.2 Extend `filteredDateGroups` to a single `keep` predicate combining artist (OR) AND journey (OR), preserving the `!!c.artistId` ghost-card guard
- [ ] 2.3 Replace the per-array URL sync with a single watcher that writes both `artists` and `journey` params in one `history.replaceState` (avoid double write)
- [ ] 2.4 Add `@computed('dateGroups','followedArtists') get countedArtists` building counts over the unfiltered `dateGroups`, projecting to `{id,name,count}`, hiding `count === 0`, sorting by count desc then name asc
- [ ] 2.5 Expose `isAuthenticated` to the template for journey-facet gating
- [ ] 2.6 Unit-test the filter predicate (artist-only, journey-only, both, no-status excluded) and the count/sort/hide-zero derivation

## 3. Filter bar UI — journey facet, counted artist chips, guest gating

- [ ] 3.1 Bind `counted-artists` into `artist-filter-bar`; render the count prefix on each artist chip with `key.bind="artist.id"` on the repeat
- [ ] 3.2 Add a journey-status `<section>` (own `<h*>` + `aria-labelledby`) with multi-select chips driven by a `pendingStatuses` array and `JOURNEY_STATUS_CONFIG`, ordered with the process/outcome line break
- [ ] 3.3 Add `selected-statuses` two-way bindable and commit it in `confirmSelection()`; make `clearAll()` also clear pending statuses and `hasPendingSelection` consider both facets
- [ ] 3.4 Gate the journey `<section>` with `if.bind="showJourneyFacet"` (bound to `isAuthenticated`); keep the outer `!isOnboarding` guard and confirm the artist facet renders for guests
- [ ] 3.5 Style selected journey chips with `--journey-hue-*` fill and unselected as neutral outlines retaining icon + label (cube-css layers; confirm hue token naming with the cube-css skill)

## 4. Tests and verification

- [ ] 4.1 Add/extend component smoke tests for the two-facet sheet, guest (no journey facet) vs authenticated, and counted/sorted artist chips
- [ ] 4.2 Add an e2e/integration check for URL round-trip: `?artists=…&journey=…` parses on load and a single `replaceState` writes both on confirm
- [ ] 4.3 Run `make check`; the FE Smoke path must mock backend responses (dev env is intentionally stopped — do not proxy)
- [ ] 4.4 Refresh frontend visual baselines for the intentional UI changes (counted chips, journey chips, `lost` 💔) per the baseline-refresh constraint

## 5. Ship

- [ ] 5.1 Open the frontend PR (assignee/reviewer `pannpers`), drive CI green, resolve any bot review findings, and merge
- [ ] 5.2 Archive this OpenSpec change in the specification repo once tasks are complete
- [ ] 5.3 Cut the frontend GH Release (retag → prod AR), confirm the automated prod pin-bump lands in cloud-provisioning and ArgoCD syncs, and verify the filter works in prod
