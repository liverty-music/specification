## 1. Route guard relaxation (scope A1, A2, A4, A5)

- [x] 1.1 In `auth-hook.ts`, replace the silent redirect for onboarding users hitting a future/no-tutorialStep route with a redirect + contextual `Snack` (gating-aware message; compute "あと N 組" from `DASHBOARD_FOLLOW_TARGET - followedCount`).
- [x] 1.2 Add a Settings exception: allow `/settings` during onboarding from the `discovery` step onward (no redirect to current step).
- [x] 1.3 Add a Welcome exception: allow `/` during onboarding; relax `welcome-route.canLoad` so viewing Welcome does not bounce to the current step and does not reset `onboardingStep`.
- [x] 1.4 Rewrite the COMPLETED-guest branch (Priority 3) to allow navigation to ALL routes (free roam) instead of redirecting to landing / toasting "login required".
- [x] 1.5 Add i18n keys for the new blocked-nav snackbar copy (JA/EN).
- [x] 1.6 Vitest: update the route-guard decision-table tests for feedback paths, Settings/Welcome exceptions, and free roam after COMPLETED.

## 2. Guest-adaptive Settings (scope A3)

- [x] 2.1 In `settings-route.html`, render the ACCOUNT section conditionally: guest → "ログイン / 新規登録" CTA; authenticated → existing email/verification/sign-out.
- [x] 2.2 Hide email-verification rows and Sign Out for guests; wire the CTA to `authService.signIn()` / `signUp()`.
- [x] 2.3 For guests, make language change apply via `I18N.setLocale()` only (skip `UserService.UpdatePreferredLanguage`); source home-area from guest storage. (changeLocale already routes by auth state; currentHome now reads guest storage for guests.)
- [x] 2.4 Add i18n keys for the guest auth-entry CTA (JA/EN).
- [x] 2.5 Vitest: guest vs authenticated Settings rendering; guest language change does not call the backend RPC.

## 3. (Dropped) Completion trigger on My Artists arrival — scope A6

Dropped during review: `main` merged the analytics-consent feature, which inserts a `CONSENT`
step between MY_ARTISTS and COMPLETED. Completing on My Artists arrival would skip the consent
screen, so this change makes no `my-artists-route` completion changes and leaves the
MY_ARTISTS → COMPLETED transition to the consent-step flow.

## 4. Celebration revival, two-tier (scope B)

- [x] 4.1 Add `@bindable confetti = true` to `celebration-overlay.ts`; gate the confetti container with `if.bind="confetti"` in the template.
- [x] 4.2 Implement `maybeCelebrate()` in `dashboard-route.ts`, gated on `!needsRegion` + data ready + a localStorage "shown" flag (per tier).
- [x] 4.3 Call `maybeCelebrate()` from both `attached()` (when `!needsRegion`) and `onHomeSelected()` (after `loadData` resolves).
- [x] 4.4 Z-light: guest first dashboard → overlay with `confetti=false`. Z-full: post-signup (`liverty:postSignup:shown` pending) → overlay with `confetti=true`, then open PostSignupDialog on dismissal.
- [x] 4.5 Render `<celebration-overlay>` in `dashboard-route.html` with the tier bindings; add celebration i18n strings (JA/EN).
- [x] 4.6 Vitest: maybeCelebrate fires once per tier, only after region+data; reduced-motion skips confetti; post-signup sequences celebration → PostSignupDialog.

## 5. Drift cleanup (scope C)

- [x] 5.1 Delete `src/services/nav-dimming-service.ts` and its registration in `main.ts`; remove the `navDimming` injection and `setDimmed(false)` call in `dashboard-route.ts`. (Also removed the orphaned `test/helpers/mock-nav-dimming-service.ts`.)
- [x] 5.2 Confirm `celebration-overlay` is now actually rendered (no longer dead code) and keep its `main.ts` registration.
- [ ] 5.3 Delete the dead `openspec/specs/dashboard-lane-introduction/spec.md` capability at archive time (all requirements already tombstoned).
- [x] 5.4 Correct `openspec/specs/state-transition-diagram/spec.md`: remove the `detail` state and the "Generate Dashboard CTA" transition; refresh the mermaid diagram. (Dashboard arrival advances to my-artists; the MY_ARTISTS → COMPLETED transition is left as-is for the consent-step flow.)

## 6. Verification

- [x] 6.1 Run `make check` (lint + test) in `frontend`; fix any failures. (Exit 0: 1129 tests pass, tsc + biome + brand-vocabulary + templates clean.)
- [x] 6.2 Confirm the CI Playwright suites pass — they run against a mocked local build (no dev-environment dependency, per the intentionally-stopped dev env): E2E, Smoke, and Visual Regression all green on the merged commit. (No dev-server / manual walkthrough tasks: the dev environment is intentionally stopped, so dev-dependent verification is out of scope.)

## 7. Spec sync & PR

- [x] 7.1 Confirm `openspec validate relax-onboarding-routing` passes.
- [x] 7.2 Open the specification PR with a Conventional Commit message linking the tracking issue (`Refs: #542`). (PR #543 — merged.)
