## Context

`ToastNotification` is a single class serving as both a DI singleton (`IToastService`) and a custom element (`<toast-notification>`). The DI singleton instance never gets its template rendered, so `containerElement` (set via `ref` binding) is always `undefined`, causing `TypeError` when `show()` calls `hidePopover()`.

The element is placed only inside `discover-page.html`, but `IToastService.show()` is called from 8+ locations across the app (settings, auth-hook, error-banner, etc.), meaning toasts silently fail on all pages except discover.

Aurelia 2's `IEventAggregator` provides a built-in pub/sub mechanism designed for exactly this pattern: cross-cutting, fire-and-forget notifications where the publisher and subscriber don't need to know about each other.

## Goals / Non-Goals

**Goals:**
- Eliminate the DI singleton / custom element dual-instance bug
- Make toast work from any page (app-level placement)
- Follow Aurelia 2 idiomatic patterns (EA for notifications, DI for shared state)
- Keep the same developer ergonomics (one-line call to show a toast)

**Non-Goals:**
- Changing toast visual design or animations
- Adding toast features (stacking limits, action buttons, custom templates)
- Refactoring error-banner (separate concern, uses `<dialog>` correctly)

## Decisions

### 1. Use `IEventAggregator` with typed event class instead of DI singleton

**Decision**: Replace `IToastService` with a `Toast` event class published via `IEventAggregator`.

**Why over DI service**: Toast is fire-and-forget — callers don't read toast state, don't await results, and don't need a reference to the toast component. This is the textbook pub/sub use case. Aurelia 2 docs demonstrate this exact pattern with `ToastCenter` subscribing to typed events.

**Why over DOM CustomEvent**: `IEventAggregator` is framework-aware, provides `IDisposable` for cleanup, and supports typed event classes. DOM events require manual bubbling and lack type safety.

### 2. Typed event class over string channel

**Decision**: Use `class Toast { constructor(public message: string, public severity: ToastSeverity = 'info', public durationMs = 2500) {} }` instead of `ea.publish('toast:show', data)`.

**Why**: Aurelia 2's EA supports class-based subscriptions (`ea.subscribe(Toast, handler)`), providing compile-time type safety and IDE autocompletion. String-based channels lose type information and risk typos.

### 3. Place `<toast-notification>` in `my-app.html` as app-level overlay

**Decision**: Move from `discover-page.html` to `my-app.html`, alongside existing app-level overlays (`<error-banner>`, `<pwa-install-prompt>`).

**Why**: Toast is an app-wide concern. Placing it in the app shell ensures it's always in the DOM regardless of active route. This matches the existing pattern for `<error-banner>`.

### 4. Custom element owns all DOM operations

**Decision**: `ToastNotification` custom element subscribes to events in `attaching()`, manages its own `toasts[]` array, and handles Popover API calls (`showPopover()`/`hidePopover()`) internally.

**Why**: This follows Aurelia's separation of concerns — DOM operations belong in the custom element, not in services. The element manages its own lifecycle via `attaching()`/`detaching()` with proper `IDisposable` cleanup.

## Risks / Trade-offs

**[Slightly more verbose call site]** → Callers change from `this.toastService.show(msg, severity)` to `this.ea.publish(new Toast(msg, severity))`. Marginally more characters, but the import is simpler (`Toast` event class vs `IToastService` interface) and the semantic intent is clearer.

**[No delivery guarantee]** → If `<toast-notification>` is not in the DOM (e.g., during app bootstrap), published events are silently dropped. → Mitigated by placing the element in `my-app.html` which is always present. Edge case: toasts fired during initial route resolution before `attaching()` completes could be missed — acceptable for notification UX.

**[IEventAggregator is a new dependency pattern]** → This codebase currently doesn't use EA. → `IEventAggregator` is a core Aurelia 2 feature (no install needed). Introducing it for toast establishes a clean pattern for future cross-cutting notifications.
