## 1. Entity layer: extract business logic

- [x] 1.1 Add `isHypeMatched()`, `HYPE_ORDER`, `LANE_ORDER` to `entities/concert.ts`; remove from `services/dashboard-service.ts`; update imports in `dashboard-service.ts`
- [x] 1.2 Add `hasFollow()` to `entities/follow.ts`; update `state/reducer.ts` to delegate duplicate check to `hasFollow()`
- [x] 1.3 Create `entities/onboarding.ts` with `OnboardingStep`, `STEP_ORDER`, `stepIndex()`, `isOnboarding()`, `isCompleted()`, `normalizeStep()`; move from `services/onboarding-service.ts`; update imports in `onboarding-service.ts`, `state/app-state.ts`, `state/actions.ts`, `state/middleware.ts`
- [x] 1.4 Move `codeToHome()`, `displayName()`, `translationKey()` from `constants/iso3166.ts` to `entities/user.ts`; add re-exports in `constants/iso3166.ts` for backward compatibility
- [x] 1.5 Move `bytesToHex()`, `bytesToDecimal()`, `uuidToFieldElement()` from `services/proof-service.ts` to `entities/entry.ts`; update imports in `proof-service.ts`
- [x] 1.6 Update `entities/index.ts` barrel exports with new functions and `onboarding.ts` types

## 2. View adapter layer: presentation logic

- [x] 2.1 Create `adapter/view/artist-color.ts` by moving `artistHue()`, `artistColor()`, `artistHueFromColorProfile()` from `components/live-highway/color-generator.ts`
- [x] 2.2 Create `adapter/view/hype-display.ts` by moving `HYPE_TIERS` from `routes/my-artists/my-artists-route.ts`
- [x] 2.3 Update all import sites: `dashboard-route.ts`, `event-card.ts`, `orb-renderer.ts`, `my-artists-route.ts`, `hype-inline-slider.ts` and any other files that import from the old locations
- [x] 2.4 Delete `components/live-highway/color-generator.ts` after all imports are migrated

## 3. Tests

- [x] 3.1 Add unit tests for `isHypeMatched()` in `entities/concert.spec.ts`
- [x] 3.2 Add unit tests for `hasFollow()` in `entities/follow.spec.ts`
- [x] 3.3 Add unit tests for `stepIndex()`, `isOnboarding()`, `isCompleted()`, `normalizeStep()` in `entities/onboarding.spec.ts`
- [x] 3.4 Add unit tests for `codeToHome()`, `displayName()` in `entities/user.spec.ts`
- [x] 3.5 Add unit tests for `bytesToHex()`, `bytesToDecimal()`, `uuidToFieldElement()` in `entities/entry.spec.ts`
- [x] 3.6 Add unit tests for `artistHue()`, `artistColor()`, `artistHueFromColorProfile()` in `adapter/view/artist-color.spec.ts`

## 4. Verification

- [x] 4.1 Run `make check` (lint + test) and fix any issues
- [x] 4.2 Remove backward-compatibility re-exports from `constants/iso3166.ts` if no remaining direct importers — **deferred**: 6 files still import from `constants/iso3166.ts`; re-exports remain
