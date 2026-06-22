## Context

The PostSignupDialog is shown once to new users after sign-up. It currently offers a PWA install row when `PwaInstallService.canShowFab` is true — a condition that requires both onboarding completion and a captured `beforeinstallprompt` event.

Two problems compound to cause the install row to intermittently not appear:

**Problem 1 — Construction race**: `PwaInstallService` is a lazily-resolved DI singleton, first constructed when `PwaInstallFab` binds. `PwaInstallFab` is guarded by `if.bind="showNav"` which is `false` during the `/auth/callback` route. Chrome fires `beforeinstallprompt` early during the page load that lands on `/auth/callback` — before `PwaInstallFab` binds or `PwaInstallService` is constructed. The event is silently lost.

**Problem 2 — Condition over-restriction**: Even when the event is not captured (Chrome engagement cooldown, previous dismissal, etc.), the current design hides the install row entirely. Users with a PWA-capable browser have no install path in the dialog.

The `PwaInstallFab` is unaffected — it shows whenever `canShowFab` is true. FAB semantics are preserved.

## Goals / Non-Goals

**Goals:**
- Register the `beforeinstallprompt` listener before any routing by eagerly constructing `PwaInstallService` in `AppShell`
- Show the install row in the PostSignupDialog for all PWA-capable browsers (Chrome/Edge) regardless of whether the native prompt has been captured
- Show browser menu install instructions as fallback when the native prompt is unavailable
- Reliably update the dialog row when the native prompt arrives after the dialog opens

**Non-Goals:**
- Change FAB behavior or `canShowFab` semantics
- Add install guidance for browsers without `BeforeInstallPromptEvent` (Firefox, etc.)
- Introduce a new screen or route for install instructions

## Decisions

### Decision: Eager construction via AppShell

`AppShell` resolves `IPwaInstallService` in its class body (a private field used only for construction side-effect). `AppShell` activates before any routing, so the `beforeinstallprompt` event listener is registered before Chrome can fire the event.

**Alternative considered**: Register the listener in `main.ts` before Aurelia bootstraps, storing the event in a module-level buffer. Rejected — it splits the service's construction and event handling, and `AppShell` activation already reliably precedes routing in Aurelia's lifecycle.

### Decision: New `canShowInstallOption` getter — decouple dialog condition from `canShowFab`

A new `canShowInstallOption` getter is added to `PwaInstallService`:

```
browserSupportsPwa     = 'BeforeInstallPromptEvent' in window
canShowInstallOption   = !installed && browserSupportsPwa
```

The PostSignupDialog uses `canShowInstallOption` for row visibility; `canShowFab` is unchanged for the FAB. iOS is automatically excluded because iOS browsers lack `BeforeInstallPromptEvent` (`browserSupportsPwa = false`), so `!isIos` becomes implicit and no separate iOS guard is needed in the dialog.

**Alternative considered**: Relax the `deferredPrompt !== null` requirement inside `canShowFab`. Rejected because `canShowFab` drives the FAB, and a FAB without `deferredPrompt` would silently no-op on tap for non-iOS. The FAB and dialog have legitimately different semantics.

### Decision: Inline instruction expansion, no new bottom-sheet

When the native prompt is unavailable, the install row shows a "How to add" button. Tapping it expands numbered instructions inline (browser menu → Add to Home Screen). No nested bottom-sheet.

**Alternative considered**: Reuse `pwa-install-fab`'s iOS instruction sheet. Rejected — the dialog is itself a bottom-sheet; nesting creates z-index complexity. Inline expansion is simpler and consistent with the dialog's visual register.

### Decision: Explicit `@watch` on `canShowFab` in PostSignupDialog

`PostSignupDialog` adds `@watch((vm) => vm.pwaInstall.canShowFab)` to drive an `@observable canInstallNatively` field. The template binds to `canInstallNatively` rather than a plain getter.

**Why**: `if.bind` / attribute bindings on a plain getter that traverses an injected service's `@observable` property depend on Aurelia's expression observer tracking the cross-object dependency. Explicit `@watch` on a ViewModel is guaranteed to fire synchronously on change; dirty-check polling is not.

## Risks / Trade-offs

- **AppShell `_pwaInstall` is "dead" from the template's perspective** — a reviewer may flag it as unused. A brief comment explains the construction-side-effect intent.
- **Instruction row visible even during Chrome's 3-month prompt cooldown** — the fallback instructions appear, which is correct UX (the user can still install manually). The row does not promise a one-tap experience when the prompt is suppressed.
- **Instruction steps are Chrome/Edge-centric** — Samsung Internet and other `BeforeInstallPromptEvent` browsers have similar enough menu flows ("Add to Home Screen") that the generic steps are usable.
