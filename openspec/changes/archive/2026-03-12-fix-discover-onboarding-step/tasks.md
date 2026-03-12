## 1. Auth Hook Fix

- [x] 1.1 Refactor `AuthHook.canLoad()` in `src/hooks/auth-hook.ts`: change the `auth: false` short-circuit to only apply when `tutorialStep` is absent. Routes with both `auth: false` and `tutorialStep` SHALL proceed to the tutorial step logic.
- [x] 1.2 Add handling for `auth: false` + `tutorialStep` routes when no active tutorial session exists (onboardingStep unset/0): redirect to landing page.

## 2. Route Configuration

- [x] 2.1 Add `tutorialStep: 1` to the `/discover` route data in `src/my-app.ts`: change `data: { auth: false }` to `data: { auth: false, tutorialStep: 1 }`.

## 3. Tests

- [x] 3.1 Update or add auth-hook unit tests to cover: public route with `tutorialStep` during active tutorial allows navigation.
- [x] 3.2 Add auth-hook unit test: public route with `tutorialStep` but no active tutorial redirects to landing page.
- [x] 3.3 Verify existing auth-hook tests still pass (pure `auth: false` routes without `tutorialStep` remain unaffected).

## 4. Spec Alignment

- [x] 4.1 Update `openspec/specs/frontend-route-guard/spec.md` with the modified requirements from this change's delta spec (route path `/discover` instead of `/onboarding/discover`, auth hook behavior for `auth: false` + `tutorialStep` routes).
