## 1. Create PromptCoordinator Service

- [x] 1.1 Create `frontend/src/services/prompt-coordinator.ts` with `IPromptCoordinator` DI interface and `PromptCoordinator` singleton class
- [x] 1.2 Implement in-memory `shownPromptType: string | null` field that tracks which prompt (if any) has been displayed this session
- [x] 1.3 Implement `canShowPrompt(type: 'notification' | 'pwa-install'): boolean` -- returns `true` only if no prompt has been shown this session
- [x] 1.4 Implement `markShown(type: 'notification' | 'pwa-install'): void` -- records the prompt type shown this session
- [x] 1.5 Implement priority logic: if both prompts query eligibility, notification wins (notification prompt checks first due to attached lifecycle running before PwaInstallService re-evaluation)
- [x] 1.6 Register `IPromptCoordinator` in `main.ts` DI container

## 2. Update PwaInstallService with Guards

- [x] 2.1 Add `IOnboardingService` as a constructor dependency via `resolve(IOnboardingService)`
- [x] 2.2 Add `IAuthService` as a constructor dependency via `resolve(IAuthService)`
- [x] 2.3 Add `IPromptCoordinator` as a constructor dependency via `resolve(IPromptCoordinator)`
- [x] 2.4 Update `evaluateVisibility()` to require `this.onboarding.isCompleted === true`
- [x] 2.5 Update `evaluateVisibility()` to require `this.auth.isAuthenticated === true`
- [x] 2.6 Update `evaluateVisibility()` to require `this.promptCoordinator.canShowPrompt('pwa-install') === true`
- [x] 2.7 Persist `completedSessionCount` to LocalStorage when onboarding completes, and gate PWA install on `sessionCount >= completedSessionCount + 2`
- [x] 2.8 Call `this.promptCoordinator.markShown('pwa-install')` when `canShow` transitions to `true`

## 3. Update NotificationPrompt with Guards

- [x] 3.1 Add `IAuthService` as a dependency via `resolve(IAuthService)`
- [x] 3.2 Add `IOnboardingService` as a dependency via `resolve(IOnboardingService)`
- [x] 3.3 Add `IPromptCoordinator` as a dependency via `resolve(IPromptCoordinator)`
- [x] 3.4 Update `attached()` to return early if `!this.auth.isAuthenticated`
- [x] 3.5 Update `attached()` to return early if `!this.onboarding.isCompleted`
- [x] 3.6 Update `attached()` to return early if `!this.promptCoordinator.canShowPrompt('notification')`
- [x] 3.7 Call `this.promptCoordinator.markShown('notification')` when `isVisible` is set to `true`

## 4. Move Notification Prompt to App Shell

- [x] 4.1 Remove `<import from="../components/notification-prompt/notification-prompt">` from `dashboard.html`
- [x] 4.2 Remove `<notification-prompt>` element from `dashboard.html`
- [x] 4.3 Add `<import from="./components/notification-prompt/notification-prompt">` to `my-app.html`
- [x] 4.4 Add `<notification-prompt if.bind="auth.isAuthenticated && onboarding.isCompleted && showNav">` to `my-app.html`, placed after `<pwa-install-prompt>` and before `<main>`
- [x] 4.5 Inject `IAuthService` into `MyApp` class (add `private readonly auth = resolve(IAuthService)`)
- [x] 4.6 Verify `IOnboardingService` is already injected in `MyApp` (it is -- `this.onboarding`)

## 5. Tests

- [x] 5.1 Unit test `PromptCoordinator`: verify `canShowPrompt` returns `true` initially, `false` after `markShown` for a different type
- [x] 5.2 Unit test `PromptCoordinator`: verify `canShowPrompt` returns `false` for any type after another type is marked shown
- [x] 5.3 Unit test `PwaInstallService`: verify `canShow` remains `false` when `onboarding.isCompleted` is `false`
- [x] 5.4 Unit test `PwaInstallService`: verify `canShow` remains `false` when `auth.isAuthenticated` is `false`
- [x] 5.5 Unit test `PwaInstallService`: verify `canShow` remains `false` when `promptCoordinator.canShowPrompt` returns `false`
- [x] 5.6 Unit test `PwaInstallService`: verify `canShow` becomes `true` when all guards pass and `sessionCount >= completedSessionCount + 2`
- [x] 5.7 Unit test `NotificationPrompt`: verify `isVisible` remains `false` when `auth.isAuthenticated` is `false`
- [x] 5.8 Unit test `NotificationPrompt`: verify `isVisible` remains `false` when `onboarding.isCompleted` is `false`
- [x] 5.9 Unit test `NotificationPrompt`: verify `isVisible` becomes `true` when all guards pass and notification permission is not `granted`

## 6. Verification

- [x] 6.1 Run `make lint` in frontend to confirm no lint errors
- [x] 6.2 Run `make test` in frontend to confirm all unit tests pass
- [x] 6.3 Manual test: start fresh (clear LocalStorage), walk through onboarding Steps 1-6 -- confirm no prompts appear
- [x] 6.4 Manual test: complete onboarding, reload page -- confirm notification prompt appears (not PWA install)
- [x] 6.5 Manual test: dismiss notification prompt, reload page again -- confirm PWA install prompt appears on subsequent eligible session
- [x] 6.6 Manual test: verify both prompts never appear simultaneously in the same session
