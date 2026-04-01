## Context

The onboarding flow on the dashboard has three interacting bugs:

1. **Incorrect auto-open**: `PageHelp.attached()` auto-opens the help bottom-sheet on ALL pages during onboarding, but the spec only defines auto-open for Discovery and My Artists. On Dashboard, page-help should only display the `?` icon (manual open). The unconditional auto-open during celebration produces a dark, unreadable screen with two overlapping overlays.

2. **Positioning**: The `<page-help>` component is placed at the bottom of the dashboard template (outside the page header), causing the `?` icon to appear at the bottom-left. Additionally, discovery has no `<page-help>` at all despite the spec requiring it. Only my-artists correctly places page-help inside `<page-header>`.

3. **Orchestration inversion**: `loading()` sets `showCelebration = true` immediately, which prevents `attached()` from calling `startLaneIntro()` (guarded by `!showCelebration`). After celebration dismiss, there is no code to trigger lane intro. The result: lane intro never executes, and users are stuck without guidance.

The existing specs clearly define the correct order: lane intro (HOME → NEAR → AWAY) → celebration → free exploration. The code needs to match this.

## Goals / Non-Goals

**Goals:**
- Fix the orchestration so lane intro runs before celebration (matching the spec)
- Limit page-help auto-open to Discovery and My Artists only (matching the spec)
- Unify `<page-help>` placement: all onboarding pages use `<page-header>` with page-help inside its slot
- Add regression tests that fail against the current bugs and pass after fixes

**Non-Goals:**
- Redesigning the onboarding flow or adding new steps
- Changing the page-help content or styling
- Modifying the celebration overlay animation

## Decisions

### D1: Restrict page-help auto-open to spec-defined pages

**Decision**: Add an `autoOpenPages` allowlist (`['discovery', 'my-artists']`) inside `PageHelp.attached()`. Only pages in the allowlist trigger auto-open. Dashboard page-help shows the `?` icon only — manual open.

**Why not a `suppress` bindable?** The spec clearly defines which pages auto-open. This is a property of the page-help component's own logic, not something the parent should control. An allowlist is simpler, self-documenting, and doesn't require plumbing from each route.

### D2: Remove premature `showCelebration` from `loading()`, trigger after lane intro

**Decision**: `loading()` no longer sets `showCelebration = true`. Instead, `completeLaneIntro()` (called after AWAY phase tap) sets `showCelebration = true`. The `attached()` method always calls `startLaneIntro()` when the step is DASHBOARD.

**Flow after fix:**
```
loading()
  └─ set needsRegion, loadData()

attached()
  └─ isOnboardingStepDashboard → startLaneIntro()
       └─ HOME → NEAR → AWAY (tap-to-advance)
       └─ completeLaneIntro() → showCelebration = true
            └─ onCelebrationOpen() → setStep(MY_ARTISTS)
            └─ onCelebrationDismissed() → free exploration
```

**Alternative considered**: Keep `showCelebration` in `loading()` but call `startLaneIntro()` in `onCelebrationDismissed()`. Rejected — contradicts the spec which says celebration is AFTER lane intro, not before.

### D3: Unify page-help placement inside `<page-header>` on all pages

**Decision**: All onboarding pages (dashboard, discovery, my-artists) use `<page-header>` with `<page-help>` inside its `<au-slot>`. The `<page-header>` component uses `display: flex` with `h1 { flex: 1 }`, so slot content is automatically right-aligned.

- **dashboard**: Add `<page-header>` above the stage header. Title TBD (e.g., `nav.home` or similar existing i18n key). Place `<page-help page="dashboard">` inside.
- **discovery**: Add `<page-header>` above the search bar. Place `<page-help page="discovery">` inside.
- **my-artists**: Already correct — no changes needed.

### D4: Test-first approach

**Decision**: Write failing unit tests first that detect the bugs, then implement fixes. This ensures:
- Bugs are reproducible
- Fixes are verified by the same tests passing
- Future regressions are caught

## Risks / Trade-offs

- **[Risk] Lane intro depends on data being loaded** → `startLaneIntro()` already awaits `dataPromise`, so this is handled. If data fetch fails, lane intro is skipped and celebration shows directly (per spec).
- **[Risk] `celebrationShown` localStorage flag prevents re-testing** → Tests clear localStorage between runs.
- **[Risk] Dashboard `<page-header>` changes visual layout** → The header is minimal (flex row with title + slot). Visual impact is small and consistent with other pages.
