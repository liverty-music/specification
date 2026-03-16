## Why

The state management layer introduced in `introduce-state-management` uses inconsistent naming that reduces readability and maintainability:

1. **`OnboardingStep` uses numeric values** — localStorage stores `'3'` which is meaningless without code reference, and step reordering causes bugs. Numeric range comparison (`step >= 1 && step <= 5`) is fragile.
2. **`guestArtists` vs `guest/` namespace mismatch** — Actions use the `guest/` prefix but the state slice is `guestArtists`.
3. **`tutorial` vs `onboarding` terminology split** — Route data uses `tutorialStep`, getters use `isTutorialStep3`, but the service is `OnboardingService`. The codebase should use one term consistently.
4. **Legacy steps `LOADING` and `SIGNUP` remain** — These steps were removed in prior changes but their enum values were kept for backward compatibility that is no longer needed.
5. **Logging middleware uses `console.log`** — Should use Aurelia's `ILogger` for consistency with the rest of the application.

## What Changes

- **BREAKING**: `OnboardingStep` values change from numbers to string names (e.g., `0` → `'lp'`, `1` → `'discovery'`)
- **BREAKING**: Remove `LOADING` (step 2) and `SIGNUP` (step 6) from `OnboardingStep`
- Rename `DISCOVER` → `DISCOVERY` in `OnboardingStep`
- Rename `guestArtists` → `guest` in `AppState` and all references; `GuestArtistsState` → `GuestState`
- Rename all `tutorial` references to `onboarding` (route data, getters, methods, comments, i18n)
- Refactor logging middleware to accept `ILogger` via factory function
- Add mermaid state transition diagram as spec documentation
- Add comprehensive edge-case unit tests for all state transitions

## Capabilities

### New Capabilities

- `state-transition-diagram`: Mermaid state machine diagrams documenting all reducer state transitions for onboarding and guest state

### Modified Capabilities

- `state-management`: AppState slice rename (`guestArtists` → `guest`), OnboardingStep string values, remove legacy steps, logger middleware refactor
- `onboarding-tutorial`: Rename all `tutorial` references to `onboarding`, remove LOADING/SIGNUP step scenarios, update step values from numeric to string
- `frontend-onboarding-flow`: Update guest artist storage references from `guestArtists` to `guest`

## Impact

- **Frontend state layer**: `app-state.ts`, `actions.ts`, `reducer.ts`, `middleware.ts`, `store-interface.ts`
- **Frontend services**: `onboarding-service.ts`, `local-artist-client.ts`, `guest-data-merge-service.ts`, `follow-service-client.ts`, `concert-service.ts`
- **Frontend routes**: `app-shell.ts`, `auth-hook.ts`, `dashboard-route.ts`, `discovery-route.ts`, `my-artists-route.ts`, `welcome-route.ts`, `auth-callback-route.ts`
- **Frontend components**: `coach-mark.html`, `user-home-selector.ts`
- **Frontend i18n**: `translation.json` (user-facing text)
- **Frontend tests**: All test files referencing `guestArtists`, `tutorial`, or `OnboardingStep` numeric values
- **localStorage**: Stored step values change from numbers to strings (no backward compat migration)
