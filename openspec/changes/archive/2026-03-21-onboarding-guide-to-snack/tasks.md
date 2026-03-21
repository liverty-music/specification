## 1. Template and ViewModel cleanup

- [x] 1.1 Remove `<dialog popover="auto" class="onboarding-guide">` element from `discovery-route.html`
- [x] 1.2 Remove `onboardingGuide` ref property from `discovery-route.ts`
- [x] 1.3 Remove `showPopover()` call from `attached()` in `discovery-route.ts`
- [x] 1.4 Inject `IEventAggregator` and `I18N` into `DiscoveryRoute` (if not already injected)
- [x] 1.5 Publish `new Snack(this.i18n.tr('discovery.popoverGuide'), 'info', { duration: 5000 })` in `attached()` when `isOnboarding` is true

## 2. CSS cleanup

- [x] 2.1 Remove `.onboarding-guide` CSS block from `discovery-route.css` (including `@starting-style`, `:popover-open`, `::backdrop` rules)

## 3. Unit tests

- [x] 3.1 Remove `showPopover` mock tests from `discovery-route.spec.ts`
- [x] 3.2 Add test: when onboarding, `attached()` publishes a `Snack` event with correct message, severity `info`, and duration `5000`
- [x] 3.3 Add test: when not onboarding, `attached()` does not publish a `Snack` event

## 4. E2E tests

- [x] 4.1 Update `onboarding-flow.spec.ts` Step 1 assertions: replace `.onboarding-guide` popover checks with snack-bar `.snack-item` visibility assertions
- [x] 4.2 Remove light-dismiss test (click-outside-to-close) — replaced by auto-dismiss behavior

## 5. Verification

- [x] 5.1 Run `make check` in frontend (lint + test)
- [x] 5.2 Run `npx playwright test onboarding-flow` to verify E2E
