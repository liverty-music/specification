## 1. Delete loading-sequence route and service

- [x] 1.1 Delete `frontend/src/routes/onboarding-loading/loading-sequence.ts`
- [x] 1.2 Delete `frontend/src/routes/onboarding-loading/loading-sequence.html`
- [x] 1.3 Delete `frontend/src/routes/onboarding-loading/loading-sequence.css`
- [x] 1.4 Delete `frontend/src/services/loading-sequence-service.ts`

## 2. Remove route and step references

- [x] 2.1 Remove the `onboarding/loading` route entry from `frontend/src/my-app.ts`
- [x] 2.2 Update the `OnboardingStep.LOADING` route mapping in `frontend/src/services/onboarding-service.ts` to point to `'dashboard'` instead of `'onboarding/loading'`

## 3. Remove i18n keys

- [x] 3.1 Remove `loading` key block from `frontend/src/locales/ja/translation.json`
- [x] 3.2 Remove `loading` key block from `frontend/src/locales/en/translation.json`

## 4. Update specs

- [x] 4.1 Delete `specification/openspec/specs/loading-sequence/` directory
- [x] 4.2 Apply delta spec to `specification/openspec/specs/onboarding-tutorial/spec.md` — remove Step 2 scenario
- [x] 4.3 Apply delta spec to `specification/openspec/specs/frontend-onboarding-flow/spec.md` — remove negative requirement about `/onboarding/loading`

## 5. Verification

- [x] 5.1 Run `make check` in frontend to verify build and lint pass
- [x] 5.2 Verify no remaining references to `loading-sequence` or `onboarding-loading` in frontend source
