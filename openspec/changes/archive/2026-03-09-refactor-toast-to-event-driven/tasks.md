## 1. Event class and custom element rewrite

- [x] 1.1 Create `Toast` event class in `src/components/toast-notification/toast.ts` with `message`, `severity`, `durationMs` properties
- [x] 1.2 Rewrite `ToastNotification` custom element to subscribe to `Toast` events via `IEventAggregator` in `attaching()`, dispose in `detaching()`, and manage its own `toasts[]` array and Popover API calls
- [x] 1.3 Remove `IToastService` interface and DI registration exports from `toast-notification.ts`

## 2. Move element to app shell

- [x] 2.1 Add `<toast-notification>` to `my-app.html` as app-level overlay (alongside `<error-banner>`)
- [x] 2.2 Remove `<toast-notification>` and its `<import>` from `discover-page.html`
- [x] 2.3 Remove `toast-notification { position: absolute; }` from `discover-page.css`

## 3. Migrate callers to EventAggregator

- [x] 3.1 Update `discover-page.ts`: replace `resolve(IToastService)` with `resolve(IEventAggregator)`, change all `toastService.show(...)` to `ea.publish(new Toast(...))`
- [x] 3.2 Update `settings-page.ts`: same migration
- [x] 3.3 Update `my-artists-page.ts`: same migration
- [x] 3.4 Update `welcome-page.ts`: same migration
- [x] 3.5 Update `loading-sequence.ts`: same migration
- [x] 3.6 Update `auth-hook.ts`: same migration
- [x] 3.7 Update `error-banner.ts`: same migration

## 4. Cleanup DI registration

- [x] 4.1 Remove `IToastService` import and `.register(IToastService)` from `main.ts`

## 5. Verification

- [x] 5.1 Run `make check` (lint + typecheck + unit tests)
