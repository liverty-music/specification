## Context

The `introduce-state-management` change introduced `@aurelia/state` with a Redux-like pattern. The implementation works correctly but accumulated naming inconsistencies: numeric step values, `guestArtists` vs `guest/` namespace mismatch, and mixed `tutorial`/`onboarding` terminology. Legacy steps (`LOADING`, `SIGNUP`) were kept for backward compatibility that is no longer needed.

## Goals / Non-Goals

**Goals:**
- Consistent naming across state, actions, route data, and UI code
- String-based step values for readability in code and localStorage
- Remove dead code (legacy steps)
- Aurelia `ILogger` in logging middleware
- Mermaid state transition diagram for documentation
- Full edge-case test coverage for reducer

**Non-Goals:**
- Changing state management architecture or adding new state slices
- Backward compatibility with old numeric localStorage values
- Modifying the onboarding UX flow itself

## Decisions

### Decision 1: String step values

`OnboardingStep` values change from numbers to descriptive strings.

```typescript
// Before
export const OnboardingStep = { LP: 0, DISCOVER: 1, LOADING: 2, DASHBOARD: 3, ... }

// After
export const OnboardingStep = {
  LP: 'lp',
  DISCOVERY: 'discovery',
  DASHBOARD: 'dashboard',
  DETAIL: 'detail',
  MY_ARTISTS: 'my-artists',
  COMPLETED: 'completed',
} as const
```

**Why**: Numbers are meaningless in localStorage (`'3'` vs `'dashboard'`). Numeric range comparisons (`step >= 1 && step <= 5`) break when steps are reordered.

**Alternative**: Keep numbers but add string labels — rejected because it adds complexity without solving the localStorage readability issue.

### Decision 2: Step ordering via explicit array

Replace numeric comparison in `auth-hook.ts` (`currentStep >= tutorialStep`) with index-based comparison using an ordered array.

```typescript
const STEP_ORDER = [
  OnboardingStep.LP, OnboardingStep.DISCOVERY, OnboardingStep.DASHBOARD,
  OnboardingStep.DETAIL, OnboardingStep.MY_ARTISTS, OnboardingStep.COMPLETED,
] as const

export function stepIndex(step: OnboardingStepValue): number {
  return STEP_ORDER.indexOf(step)
}
```

**Why**: String values can't be compared with `>=`. An explicit order array makes the progression visible and easy to modify.

### Decision 3: `isOnboarding` via Set membership

Replace `step >= DISCOVER && step <= MY_ARTISTS` with a Set check.

```typescript
const ONBOARDING_STEPS = new Set([
  OnboardingStep.DISCOVERY, OnboardingStep.DASHBOARD,
  OnboardingStep.DETAIL, OnboardingStep.MY_ARTISTS,
])

public get isOnboarding(): boolean {
  return ONBOARDING_STEPS.has(this.currentStep)
}
```

**Why**: Set membership is explicit — adding/removing steps doesn't risk breaking range logic.

### Decision 4: `guestArtists` → `guest`

Rename the state slice and type to match the `guest/` action namespace.

- `AppState.guestArtists` → `AppState.guest`
- `GuestArtistsState` → `GuestState`
- All references in services, routes, tests, middleware

**Why**: Consistency between action namespace and state key.

### Decision 5: Logger factory for middleware

Middleware functions are plain functions without DI access. Create a factory that captures `ILogger` at registration time.

```typescript
// middleware.ts
export function createLoggingMiddleware(logger: ILogger) {
  return (currentState: AppState, action: unknown): AppState => {
    const a = action as { type?: string }
    logger.info('[Store]', a.type ?? 'unknown')
    return currentState
  }
}

// main.ts
const logger = container.get(ILogger).scopeTo('Store')
StateDefaultConfiguration.init(state, {
  middlewares: [
    { middleware: createLoggingMiddleware(logger), placement: 'before' },
    { middleware: persistenceMiddleware, placement: 'after' },
  ],
}, appReducer)
```

**Why**: Follows existing pattern where services use `ILogger.scopeTo()`. Avoids service locator anti-pattern.

**Note**: The `import.meta.env.DEV` guard moves to `main.ts` — only register the middleware in dev mode.

### Decision 6: Remove legacy steps without migration

Delete `LOADING` (was step 2) and `SIGNUP` (was step 6) entirely. No localStorage migration.

**Why**: User confirmed backward compatibility is unnecessary. Users with stale localStorage values will get an unrecognized step, which `loadPersistedState()` should handle by falling back to `LP`.

### Decision 7: `tutorial` → `onboarding` rename

Systematic rename across all code:

| Before | After |
|--------|-------|
| `tutorialStep` (route data) | `onboardingStep` |
| `isTutorialStep3` | `isOnboardingStepDashboard` |
| `isTutorialStep4` | `isOnboardingStepDetail` |
| `isTutorialStep5` | `isOnboardingStepMyArtists` |
| `onTutorialCardTapped` | `onOnboardingCardTapped` |
| `onTutorialMyArtistsTapped` | `onOnboardingMyArtistsTapped` |
| `isTutorialSignup` | `isOnboardingSignup` |
| `// Tutorial state` | `// Onboarding state` |
| `aria-label="Tutorial tip"` | `aria-label="Onboarding tip"` |
| i18n "completing the tutorial" | "completing onboarding" |

**Why**: The service is `OnboardingService`, the state slice is `onboarding`, the steps are `OnboardingStep`. Using `tutorial` in some places creates confusion.

### Decision 8: State transition diagram

Create a mermaid statechart diagram documenting all reducer transitions. Stored as a spec doc under `state-transition-diagram/spec.md`.

Two sub-diagrams:
1. **Onboarding state machine**: LP → DISCOVERY → DASHBOARD → DETAIL → MY_ARTISTS → COMPLETED, with spotlight sub-states
2. **Guest state machine**: empty → follows added → home set → cleared

## Risks / Trade-offs

- **[localStorage breakage]** → Users with old numeric step values will reset to LP. Acceptable since the app is pre-launch.
- **[Large diff]** → ~30 files touched across rename. Mitigated by doing each rename as a separate atomic task with `make check` between.
- **[`onOnboarding*` method names are verbose]** → Acceptable — clarity over brevity. These methods are only used within their own route classes.
