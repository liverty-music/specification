## 1. Discovery Page — Concert Data Gate

- [x] 1.1 Add `ConcertService/List` call after all concert searches complete in `discover-page.ts`: when `completedSearchCount >= followedCount`, call `ConcertService/List` and store the result count in a new `concertGroupCount` field
- [x] 1.2 Update `showDashboardCoachMark` getter to additionally require `concertGroupCount > 0`
- [x] 1.3 Add i18n keys for the zero-concert guidance message ("No upcoming events found yet — try following more artists!") in `en/translation.json` and `ja/translation.json`
- [x] 1.4 Update `guidanceMessage` getter to return the zero-concert message when `completedSearchCount >= followedCount && concertGroupCount === 0`
- [x] 1.5 Re-evaluate the concert data gate when a new artist is followed and their search completes (existing `markSearchDone` → re-call `ConcertService/List`)

## 2. Dashboard — Empty Data Fallback

- [x] 2.1 Make `startLaneIntro()` async and await `dataPromise` before checking `dateGroups.length` (already implemented — verify)
- [x] 2.2 When `dateGroups.length === 0`, skip lane intro entirely: set `laneIntroPhase = 'done'`, call `skipToMyArtists()` which sets Step 4 and activates My Artists tab spotlight (already implemented — verify)
- [x] 2.3 Add card-phase guard in `advanceLaneIntro()`: if advancing to 'card' with `dateGroups.length === 0`, skip to done and call `skipToMyArtists()` (already implemented — verify)

## 3. Coach Mark — Retry Exhaustion Cleanup

- [x] 3.1 In `coach-mark.ts` `findAndHighlight()`, replace `this.visible = false` with `this.deactivate()` when retries are exhausted after 5 seconds (already implemented — verify)

## 4. Unit Tests

- [x] 4.1 Add test TC-GATE-01: `showDashboardCoachMark` is false when `concertGroupCount === 0` despite 3+ follows and all searches complete
- [x] 4.2 Add test TC-GATE-02: `showDashboardCoachMark` is true when `concertGroupCount > 0` with 3+ follows and all searches complete
- [x] 4.3 Add test TC-GATE-03: Guidance message shows "no upcoming events" when searches complete with no concerts
- [x] 4.4 Verify test TC-GATE-04 exists: Lane intro skipped when dateGroups is empty (already implemented — verify)
- [x] 4.5 Verify test TC-GATE-05 exists: Coach mark fully deactivates on retry exhaustion (already implemented — verify)

## 5. E2E Tests

- [x] 5.1 Add E2E test TC-GATE-E2E-01: Dashboard with empty concert data skips lane intro without stuck overlay (already implemented — verify)
- [x] 5.2 Add E2E test TC-GATE-E2E-02: Discovery page does not show Dashboard coach mark when `ConcertService/List` returns empty groups

## 6. Lint & Verification

- [x] 6.1 Run `make check` (lint + unit tests) and fix any failures
- [x] 6.2 Run E2E tests against dev server and fix any failures (12/13 pass; 1 pre-existing failure in continuous flow test unrelated to this change)
