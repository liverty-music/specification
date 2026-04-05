## Context

Two independent issues are addressed together since both originate in the onboarding/dashboard area and affect the same worktree branch.

**Artist-filter layout bug**: Introduced in commit `f804195` ("feat(artist-filter): restyle checkboxes as chips with clear-all button"), the sheet content wrapper was changed from `<div class="stack filter-sheet-content">` to `<fieldset>`. The `<fieldset>` element has browser-special layout behaviour: even with `display: flex`, the `<legend>` child is lifted out of the flex flow and rendered as a block-level float-adjacent element. This causes incorrect height reporting to the parent `.sheet-body`, which breaks `scroll-snap-align: end` positioning — the sheet snaps to a position that does not align flush with the viewport bottom.

**Lane introduction removal**: The lane intro is a sequential spotlight sequence (HOME → NEAR → AWAY) activated during onboarding. Analysis shows it adds ~130 lines of state-machine code to `DashboardRoute`, introduces reactive complexity (`@watch`, `queueTask`), and coordinates with multiple services (`INavDimmingService`, `IOnboardingService`). The UX value does not justify this complexity; users can understand the lane layout from the page-help overlay.

## Goals / Non-Goals

**Goals:**
- Fix the `artist-filter-bar` bottom sheet snap alignment so the sheet is flush with the bottom of the viewport
- Fix the "全て解除" button layout (it appears misaligned because `<legend>` does not behave as a standard flex child)
- Remove the lane introduction state machine from `DashboardRoute`
- Remove associated i18n keys and dead imports

**Non-Goals:**
- Redesigning the artist filter chip UI or changing filter logic
- Changing the onboarding step progression or `OnboardingStep` enum
- Removing the celebration overlay (still triggered after `OnboardingStep.DASHBOARD` → `MY_ARTISTS` advance)
- Any backend or protobuf changes

## Decisions

### Decision: Replace `<fieldset>/<legend>` with `<section>/<h2>` (Option B)

**Chosen**: `<section aria-labelledby="filter-sheet-title">` with `<h2>` title and `<div class="sheet-header">` wrapper.

**Alternatives considered**:
- **Option A — Keep `<fieldset>`, empty `<legend>`, move header to `<div>`**: This preserves the fieldset grouping semantic but requires a hidden `<legend>` element just to satisfy the parser — a semantically odd pattern.
- **Option B — Replace with `<section>/<h2>`**: Cleaner. `<section aria-labelledby>` provides equivalent accessibility grouping. The checkbox list gets `role="group" aria-labelledby` to preserve the WAI-ARIA group semantics. `display: flex` on `<section>` behaves predictably across all browsers.

Option B is simpler, more predictable, and semantically appropriate — `<fieldset>` is designed for form field grouping with a visible label; here the label is a heading, and the interaction is confirmed by a separate button.

### Decision: Remove lane intro entirely (not gate behind a feature flag)

The lane introduction was always a one-time animation; there is no persistent user preference to toggle. Removing it unconditionally simplifies the code and avoids a flag that would only ever be turned off. The `celebrationShown` localStorage key and its helper methods (`isCelebrationShown`, `setCelebrationShown`) are also removed since they were solely used to guard against replaying the celebration inside the lane intro flow.

### Decision: Simplify `onHomeSelected` — no lane intro branch

After lane intro removal, `onHomeSelected` only needs to reload data. The `waiting-for-home` state and `laneIntroPhase` advancement logic are deleted. The home selector still works normally (for region setup) but no longer drives spotlight sequencing.

## Risks / Trade-offs

- **Celebration overlay is now orphaned**: The celebration was previously triggered by `completeLaneIntro()`. After this change, `showCelebration` is never set to `true`. The celebration overlay component remains in the template but will never open. This is intentional for this change — the celebration trigger path will be revisited separately if needed. [Risk: silent dead code] → Mitigation: the unused `showCelebration` property is still observable; a follow-up change can wire it to a new trigger or remove the overlay.
- **`dashboard-lane-introduction` spec becomes obsolete**: The spec file at `openspec/specs/dashboard-lane-introduction/spec.md` describes requirements that are now removed. The spec is updated in this change to mark the capability as removed.
- **`isOnboardingStepDashboard` getter removed**: This was the only caller of `OnboardingStep.DASHBOARD`. The enum value is not removed (it may still be used by `IOnboardingService` internals), but the getter is dead code after lane intro removal.

## Migration Plan

Frontend only. No data migration, no API changes.

1. Update `artist-filter-bar.html` and `.css`
2. Update `dashboard-route.ts`
3. Update `translation.json` (ja + en)
4. Run `make lint` and `make test` to verify
5. Merge to `306-refine-onboarding-flow` branch
