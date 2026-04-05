## REMOVED Requirements

### Requirement: Sequential Lane Header Spotlight
**Reason**: The lane introduction sequence adds significant state-machine complexity (~130 lines of code in `DashboardRoute`) without proportionate UX value. Users can understand the three-lane timetable layout through the page-help overlay. The `waiting-for-home` sub-state and `@watch`/`queueTask` coordination with data loading are removed.
**Migration**: Remove `LaneIntroPhase` type, `laneIntroPhase` / `selectedPrefectureName` properties, `startLaneIntro()`, `advanceLaneIntro()`, `completeLaneIntro()`, `updateSpotlightForPhase()`, `onLaneIntroTap()`, `laneIntroSelector`, `laneIntroMessage`, `isLaneIntroActive`, `isOnboardingStepDashboard` from `DashboardRoute`. Remove `@watch` on `dateGroups.length` and `isLoading`. Remove `queueTask` and `watch` imports. Simplify `onHomeSelected()` to only reload data. Remove `dashboard.laneIntro` keys from `ja/translation.json` and `en/translation.json`.

### Requirement: Lane Introduction State Management
**Reason**: Removed along with the lane introduction sequence. `INavDimmingService.setDimmed(true)` is no longer called at onboarding start; `setDimmed(false)` is still called on celebration dismiss.
**Migration**: Remove all `laneIntroPhase`-guarded `navDimming.setDimmed(true)` calls. The `navDimming.setDimmed(false)` call in `onCelebrationDismissed()` and `detaching()` is retained.

### Requirement: Auto-advance timer (2-second per phase) (REMOVED)
**Reason**: Already removed in a prior change. No migration needed.

### Requirement: Transition to first card spotlight after lane intro (REMOVED)
**Reason**: Already removed in a prior change. No migration needed.

### Requirement: Data loading awaited before lane intro decision (polling loop) (REMOVED)
**Reason**: Already removed in a prior change. No migration needed.
