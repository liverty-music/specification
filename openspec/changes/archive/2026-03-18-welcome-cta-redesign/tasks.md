## 1. Welcome Route ViewModel

- [x] 1.1 Remove `showGetStarted` getter from `welcome-route.ts`
- [x] 1.2 Remove `guest/clearAll` dispatch from `handleGetStarted()` (keep `onboarding/reset` and `setStep`)

## 2. Welcome Route Template

- [x] 2.1 Remove `if.bind="showGetStarted"` and `if.bind="!showGetStarted"` conditionals — render both buttons unconditionally
- [x] 2.2 Replace the `<a>` login link (`<p>` + `<a>` block) with a `<button>` element using `.welcome-btn-secondary` class
- [x] 2.3 Update i18n keys if needed (verify "Log In" label works for the secondary button)

## 3. Welcome Route Styles

- [x] 3.1 Add `.welcome-btn-secondary` style (outline/ghost variant: transparent background, subtle border, brand color text, same 48px min height as primary)
- [x] 3.2 Remove `.welcome-login-hint` and `.welcome-login-link` styles (no longer used)

## 4. Consolidate onboarding.complete()

- [x] 4.1 Remove the `if (this.onboarding.isOnboarding) { this.onboarding.complete() }` block from `auth-callback-route.ts` (lines 43-45)
- [x] 4.2 Verify `guest-data-merge-service.ts:51` remains the single call site for `onboarding/complete`

## 5. Tests

- [x] 5.1 Update welcome-route unit tests: remove tests for `showGetStarted` toggle, add tests verifying both buttons render unconditionally
- [x] 5.2 Update auth-callback-route unit tests: remove expectation for `onboarding.complete()` call in callback handler
- [x] 5.3 Run `make check` in frontend to verify lint + tests pass
