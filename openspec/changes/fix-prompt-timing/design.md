## Context

The PWA install banner and push notification prompt currently appear during the onboarding tutorial (as early as Step 3 - Dashboard) before the user has created an account or completed the guided flow. Neither prompt checks authentication or onboarding state, so they compete visually with coach marks and the region selector, and ask for permissions before the user understands the service's value.

The onboarding tutorial is designed as a linear 7-step funnel: Steps 1-5 build motivation, Step 6 prompts sign-up, and Step 7 marks completion. Permission prompts should only appear after this funnel completes, and they should not stack on top of each other.

Currently:
- `PwaInstallService.evaluateVisibility()` only checks `sessionCount >= 2` and `!isDismissed` -- no onboarding or auth awareness.
- `NotificationPrompt.attached()` only checks `!dismissed` and `permission !== 'granted'` -- no onboarding or auth awareness.
- `<notification-prompt>` is placed in `dashboard.html` (route-level), so it renders during Step 3 of onboarding when the user lands on the dashboard for the first time.
- Both prompts can appear simultaneously in the same session.

## Goals / Non-Goals

### Goals

- Prevent both prompts from appearing during onboarding Steps 1-6.
- Ensure notification prompt only appears for authenticated users.
- Show at most one permission prompt per session to avoid overwhelming the user.
- Show the notification prompt first (highest-motivation moment) and defer PWA install to a later session.
- Move `<notification-prompt>` to the app shell so it is not tied to a specific route.

### Non-Goals

- Changing the visual design of either prompt (deferred to a separate change).
- Removing z-index from prompts (neither prompt uses z-index today).
- Changing onboarding step numbers or the tutorial flow itself.
- Modifying the notification permission or PWA install browser APIs.

## Decisions

### Decision 1: Inject IOnboardingService and IAuthService into PwaInstallService

`PwaInstallService.evaluateVisibility()` will additionally require `onboarding.isCompleted === true` before setting `canShow = true`. This ensures the PWA install banner never appears during the tutorial or before authentication (since `isCompleted` requires Step 7, which requires successful sign-up at Step 6).

The service already uses Aurelia DI (`DI.createInterface` + singleton registration), so adding `IOnboardingService` and `IAuthService` as constructor dependencies follows the established pattern.

### Decision 2: Move notification-prompt from dashboard.html to my-app.html

Currently `<notification-prompt>` is imported and rendered in `dashboard.html`. This means it only appears on the dashboard route and renders during onboarding Step 3 when the user first sees the dashboard.

The prompt will move to `my-app.html` (the app shell), gated by three conditions:
- `auth.isAuthenticated` -- user has signed in
- `onboarding.isCompleted` -- tutorial is finished (Step 7)
- `showNav` -- the user is on a post-onboarding route (not landing page, loading, etc.)

This keeps the prompt visible across all authenticated post-onboarding routes, not just the dashboard.

### Decision 3: Create a PromptCoordinator singleton service

A new `PromptCoordinator` service will be registered as a DI singleton to enforce the "max 1 permission prompt per session" rule. It tracks:
- Whether any prompt has already been shown this session (in-memory flag, resets on page reload).
- Which prompt type was shown (to prevent a second prompt from appearing).

Both `PwaInstallService` and `NotificationPrompt` will call `promptCoordinator.canShowPrompt('pwa-install')` or `promptCoordinator.canShowPrompt('notification')` before displaying. Once a prompt is shown, `promptCoordinator.markShown('notification')` locks out other prompts for the session.

The coordinator does not persist state to LocalStorage -- it is session-scoped (in-memory). Each new browser session (page load) resets the coordinator, allowing a different prompt to appear.

### Decision 4: Notification prompt gets first-session priority

The notification prompt is shown on the first eligible session after onboarding completion (Step 7). At this point, the user has just signed up, motivation is highest, and push notification opt-in has the best conversion rate.

The PWA install prompt is deferred to `sessionCount >= completedSessionCount + 2`, where `completedSessionCount` is the session count at the time of onboarding completion (persisted to LocalStorage). This gives the notification prompt a clear window on the first post-completion session, and the PWA install prompt appears on a subsequent session when the user has returned and demonstrated retention.

Priority enforcement:
- `PromptCoordinator` assigns priority: notification > PWA install.
- If notification prompt is eligible, it wins. PWA install waits for the next session.
- If notification prompt was already dismissed or permission already granted, PWA install becomes eligible.

## Risks / Trade-offs

### Risk: User never sees PWA install prompt if they dismiss notification and do not return

If the user dismisses the notification prompt on their first post-completion session and never returns for a second session, they will not see the PWA install prompt. This is acceptable because a user who does not return is unlikely to install the PWA anyway. The existing `isDismissed` persistence in LocalStorage already handles this case.

### Risk: Session count drift if user clears localStorage

If the user clears LocalStorage, both `sessionCount` and `completedSessionCount` reset. The onboarding service would also reset to Step 0, so the user would re-enter the tutorial. This is existing behavior and not worsened by this change.

### Trade-off: Additional DI dependencies in PwaInstallService

Adding `IOnboardingService` and `IAuthService` as dependencies increases coupling. However, the alternative (event-based decoupling) adds complexity without meaningful benefit given the small service graph. The direct dependency is simpler and easier to test with mock injection.

### Trade-off: PromptCoordinator is session-scoped only

The coordinator uses in-memory state, so it resets on every page load. This means if a user reloads the page mid-session, the prompt could theoretically re-appear. This is acceptable because: (1) the dismiss flags in LocalStorage prevent re-showing dismissed prompts, and (2) a page reload is effectively a new session from the user's perspective.
