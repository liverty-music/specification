## Why

Toast notification uses a DI singleton (`IToastService`) that doubles as a custom element, causing a `TypeError: Cannot read properties of undefined (reading 'hidePopover')` when the DI instance (which never gets its template rendered) attempts DOM operations. Additionally, `<toast-notification>` is placed only in `discover-page.html` despite being called from 8+ locations across the app. Toast is a fire-and-forget notification — not shared state — so `IEventAggregator` (pub/sub) is the appropriate Aurelia 2 mechanism, not DI singleton.

## What Changes

- Define a `Toast` event class for type-safe pub/sub via `IEventAggregator`
- Rewrite `ToastNotification` as a self-contained custom element that subscribes to `Toast` events and manages its own DOM (Popover API, animations)
- Remove `IToastService` DI singleton and its registration from `main.ts`
- Replace all `toastService.show(...)` calls with `ea.publish(new Toast(...))`
- Move `<toast-notification>` from `discover-page.html` to `my-app.html` (app-level overlay, alongside `<error-banner>`)
- Remove `toast-notification { position: absolute; }` workaround from `discover-page.css`

## Capabilities

### New Capabilities

- `toast-event-driven`: Event-driven toast notification architecture using IEventAggregator pub/sub pattern

### Modified Capabilities

- `discover`: Remove toast-notification element and related CSS from discover page (moved to app shell)
- `app-shell-layout`: Add toast-notification as app-level overlay in my-app.html

## Impact

- **Components**: `toast-notification/` (rewrite), `error-banner/` (update import), all pages using `IToastService`
- **Services**: `IToastService` removed entirely
- **Templates**: `my-app.html` (add element), `discover-page.html` (remove element)
- **DI registration**: `main.ts` removes `IToastService` registration
- **Affected callers** (8 files): `discover-page.ts`, `settings-page.ts`, `my-artists-page.ts`, `welcome-page.ts`, `loading-sequence.ts`, `auth-hook.ts`, `error-banner.ts`, `discover-page.css`
