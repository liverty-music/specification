## Why

The guest onboarding flow is modeled as a 6-state linear machine (`LP → DISCOVERY → DASHBOARD → MY_ARTISTS → CONSENT → COMPLETED`) backed by `STEP_ORDER`, `STEP_ROUTE_MAP`, ordinal route-guard gating, a `readyForDashboard` predicate, and a mirrored discovery-count cache. Now that earlier features have been stripped, only two of these states carry product weight: a first-run guidance phase and a "first run done" flag. The machinery causes real bugs — issue #444 (hype taps after the first become unresponsive on My Artists) is a direct consequence of repurposing a hype change as the `MY_ARTISTS → CONSENT` step trigger, and a pure guest never reaches `COMPLETED` (stuck at `CONSENT` forever, `isOnboarding` latched `true`). The current code has also regressed against the `my-artists` spec, which already mandates that hype changes never revert.

## What Changes

- **BREAKING (internal state model)**: Replace the 6-state onboarding machine with a single persisted boolean. Public API stays `isOnboarding` (getter); `isCompleted` is retained as `!isOnboarding` for call-site compatibility. The persisted value uses `onboardingComplete` polarity (absent key = `false` = still onboarding). A single one-way latch `finish()` is the only mutator.
- **Adopt a soft first-run gate (Option A)**: Remove forced step ordering. The dashboard is always reachable; when a guest has no follows, the dashboard surfaces an empty-state CTA ("find artists") instead of a guard redirect.
- **Completion latch = B1 ∧ B2**: `finish()` fires on the guest's first dashboard arrival (sequenced after the light celebration, respecting the `needsRegion` deferral) and on sign-up (`auth-callback`, idempotent backstop).
- **Fix #444 at the root**: Remove the onboarding-specific branch (`setStep(CONSENT)`) and the `isOnboarding` revert guard from `onHypeInput`. Hype editing is fully decoupled from onboarding progression and always applies. This re-aligns the code with the existing `my-artists` spec.
- **Extract the coach mark into a dedicated `CoachMarkService`** (decision 2b): move spotlight state and `activate`/`deactivate`/`onTap` out of `OnboardingService`. Trigger is computed in `DiscoveryRoute` from live data: `isOnboarding && (followedCount >= 5 || artistsWithConcertsCount >= 3) && !shown`. `onTap` no longer advances any step (navigation only). Move `DASHBOARD_FOLLOW_TARGET` / `DASHBOARD_CONCERT_TARGET` to a constants module.
- **Remove**: `OnboardingStep` enum, `STEP_ORDER`, `stepIndex`, `STEP_ROUTE_MAP`, `getRouteForCurrentStep`, `normalizeStep`/`STEP_MIGRATION`, `readyForDashboard`, `setDiscoveryCounts`, the `followedCount`/`artistsWithConcertsCount` mirror, the onboarding ordinal branches of `AuthHook`, and every path that wires the `CONSENT` step into the onboarding flow.
- **Migration**: On boot, convert legacy `localStorage['onboardingStep']` once via `onboardingComplete = (step === 'completed')`, then delete the legacy key.

## Capabilities

### New Capabilities

_None._ The single-flag state fits within the existing `frontend-onboarding-flow` capability; the coach-mark extraction is an ownership change within `onboarding-spotlight`.

### Modified Capabilities

- `frontend-onboarding-flow`: Replace the linear step sequence with a single `isOnboarding` boolean; define the `finish()` completion latch (first dashboard arrival ∧ sign-up); the discovery→dashboard transition becomes a soft, non-gating navigation.
- `frontend-route-guard`: Remove onboarding ordinal gating (`tutorialStep` comparison, `readyForDashboard`, step-based redirects and their snackbars). Keep auth gating, early-unlocked routes, and free roam. The dashboard is reachable at any onboarding state.
- `onboarding-tutorial`: Remove the "Linear Step Progression" requirement; there is no forced step machine to progress through.
- `onboarding-spotlight`: The coach mark becomes a single, transient, **non-blocking** hint owned by a dedicated `CoachMarkService` (not `OnboardingService`); `onTap` performs navigation only and never advances an onboarding step; the trigger is driven by live follow/concert counts gated on `isOnboarding`. The viewport click-blocker layer, scroll lock, and multi-step continuous-spotlight persistence (all tied to the deleted step machine) are removed.
- `my-artists`: Hype changes are fully decoupled from onboarding — remove the residual "advance `onboardingStep`" effect from the guest hype-change scenario; reaffirm that hype is persisted and never reverted regardless of onboarding state.

> Note: the `state-transition-diagram` capability is a descriptive Mermaid document, not a `### Requirement:`-formatted spec, so it cannot carry a delta. Its onboarding state-machine section is refreshed to the two-state (`onboarding` → `completed`) model as a documentation task during implementation (see tasks.md), not as a spec delta file.

## Impact

- **Code (frontend)**: `services/onboarding-service.ts` (collapses to one flag), `entities/onboarding.ts` (most of it deleted), `adapter/storage/onboarding-storage.ts` (key + migration), `hooks/auth-hook.ts` (drop onboarding branches), `routes/my-artists/my-artists-route.ts` (#444 fix), `routes/discovery/discovery-route.ts` (live-count coach-mark trigger, drop count mirror), `routes/dashboard/dashboard-route.ts` (latch + empty-state CTA), `routes/welcome/welcome-route.ts` (drop `reset`/`setStep`), `routes/auth-callback/auth-callback-route.ts` (`finish()`), new `services/coach-mark-service.ts`, plus `constants/` for the targets.
- **Consumers of `isCompleted`** (`notification-prompt`, `pwa-install-service`, dashboard signup banner): unchanged — they read the retained `isCompleted` getter.
- **Out of scope**: The analytics consent screen is NOT shown. This change only removes the `CONSENT` step from the onboarding flow; the consent application logic (PostHog fail-closed default, settings opt-out toggle, `ConsentService`/`AnalyticsService`) is untouched. No coordination with the in-flight `introduce-analytics-tool` change is required.
- **Tests**: `my-artists` hype-repeat behavior (#444 regression), route-guard soft-gate behavior, coach-mark trigger from live counts, latch timing vs. celebration, legacy-key migration.
