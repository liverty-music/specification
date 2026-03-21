## Context

Three bugs in the dev environment traced to distinct root causes:

1. **TicketJourney RPC failure**: `vite.config.ts` has resolve aliases that redirect BSR-generated `TicketJourneyService` imports to `tmp/ticket-journey-stub.js` — a stub with `methods: {}`. The stub was added before the BSR release (specification v0.28.0) and never removed. `createClient()` returns an empty object, causing `this.client.setStatus is not a function`.

2. **Push notification UUID mismatch**: `PushNotificationHandler.Subscribe` passes the Zitadel `sub` claim (numeric ID `365016846690184714`) directly as `user_id` to the database. The `push_subscriptions.user_id` column is `UUID NOT NULL REFERENCES users(id)`. Other handlers (TicketHandler, UserHandler) correctly resolve via `userRepo.GetByExternalID()`.

3. **Bottom-sheet dismiss broken**: `onBackdropClick` uses `closest('.sheet-page')` to filter clicks, but `.sheet-page` has `min-block-size: 100dvh` — so the transparent area above the sheet body is inside `.sheet-page`, causing the guard to always return early. The overall implementation is overly complex with 3 dismiss paths and JS-driven backdrop opacity.

## Goals / Non-Goals

**Goals:**
- Fix all three bugs so dev environment works correctly
- Simplify bottom-sheet to use modern CSS (Scroll-Driven Animations for backdrop opacity) and reduce JS surface area
- Remove `.sheet-page` wrapper and `onBackdropClick` hack from bottom-sheet

**Non-Goals:**
- Adding touch-drag dismiss gesture (future enhancement)
- Changing the bottom-sheet's visual design or layout
- Modifying the PushNotification proto definition

## Decisions

### Decision 1: Remove Vite aliases (TicketJourney fix)

Remove the 3 resolve aliases from `vite.config.ts` and delete `tmp/ticket-journey-stub.js`. The BSR-generated code in `node_modules/@buf/liverty-music_schema.connectrpc_es` already contains the correct `TicketJourneyService` with all methods.

**Alternative considered**: Update the stub to include proper methods. Rejected — the real generated code is already installed; the alias is simply masking it.

### Decision 2: Add UserRepository to PushNotificationHandler (push notification fix)

Follow the established pattern from `TicketHandler` and `UserHandler`:

```
auth.GetUserID(ctx)  →  Zitadel sub claim (numeric string)
                     →  userRepo.GetByExternalID(ctx, externalID)
                     →  user.ID (UUIDv7)
                     →  pass to use case
```

Add `UserRepository` as a dependency to `PushNotificationHandler` and resolve the internal UUID before calling `pushUseCase.Subscribe()`. Update DI wiring in `internal/di/`.

**Alternative considered**: Convert at the use-case layer. Rejected — the handler layer is where auth context is resolved in all other handlers; consistency matters.

### Decision 3: Simplify bottom-sheet DOM — merge scroll-wrapper into dialog

**Current DOM** (5 elements, 4 levels deep):
```
dialog[popover] > div.scroll-wrapper > div.dismiss-zone + section.sheet-page > div.sheet-body > au-slot
```

**New DOM** (3 elements, 2 levels deep):
```
dialog[popover="auto"] > div.dismiss-zone + div.sheet-body > au-slot
```

The `dialog` element itself becomes the scroll-snap container (`overflow-y: auto`, `scroll-snap-type: y mandatory`). The intermediate `div.scroll-wrapper` and `section.sheet-page` are both eliminated.

**Key insight — light dismiss backdrop click does not work, but ESC does**: `popover="auto"` light dismiss via backdrop click requires clicks on `::backdrop` (outside the popover). The dialog is `inset: 0` (full-viewport) as a scroll container, so `::backdrop` has no clickable area — backdrop click dismiss is structurally impossible. However, `popover="auto"` still provides ESC key dismiss via the browser standard, which is simpler than manually handling `keydown` events with `popover="manual"`. The `toggle` event fired on ESC dismiss is used to sync the `open` state.

Changes:
- Remove `div.scroll-wrapper` — dialog itself is the scroll-snap container with `overflow-y: auto; scroll-snap-type: y mandatory; scrollbar-width: none`
- Remove `section.sheet-page` wrapper — `.sheet-body` is a direct child of `dialog` with `scroll-snap-align: end`
- Remove `onBackdropClick` method and `click.trigger` — no transparent click target ambiguity exists
- Remove `onScroll` method and `scroll.trigger` — replace JS-driven `--_backdrop-opacity` with CSS Scroll-Driven Animations using `scroll-timeline` on `dialog` and `animation-timeline` on `dialog::backdrop`
- Keep `popover="auto"` for dismissable mode — ESC key dismiss is handled by the browser; `onToggle` detects the toggle event and dispatches `sheet-closed`
- Keep `dismissableChanged` — switches between `popover="auto"` (dismissable) and `popover="manual"` (non-dismissable)
- Keep `onScrollEnd` + `scrollend.trigger` for scroll-snap dismiss detection
- Keep `dismissable` bindable — controls whether dismiss-zone is rendered and `onScrollEnd` fires

**Scroll-Driven Animation for backdrop opacity:**
```css
dialog {
  scroll-timeline: --sheet-scroll block;
}

dialog::backdrop {
  animation: backdrop-fade linear both;
  animation-timeline: --sheet-scroll;
}

@keyframes backdrop-fade {
  from { opacity: 0; }
  to   { opacity: 1; }
}
```

If `::backdrop` cannot receive `animation-timeline` from the dialog's `scroll-timeline`, fall back to static opacity (progressive enhancement).

**Alternative considered**: Use `popover="manual"` unconditionally + manual `keydown` handler for ESC. Rejected — `popover="auto"` provides ESC dismiss for free via browser standard, eliminating the need for `addEventListener('keydown')` registration/cleanup. Simpler code.

**Alternative considered**: Use touch events for swipe dismiss instead of scroll-snap. Rejected — scroll-snap provides native inertia scrolling and snap behavior; touch event reimplementation is more code and worse UX.

## Risks / Trade-offs

- **Scroll-Driven Animations on `::backdrop`**: If `::backdrop` cannot receive `animation-timeline` from the dialog's `scroll-timeline`, the backdrop opacity will be static. Dismiss functionality is unaffected. Mitigation: test in Chrome DevTools during implementation; if it doesn't work, use static `opacity: 1`.

- **No light dismiss**: Users cannot close the sheet by tapping the backdrop. Scroll-down swipe is the only dismiss mechanism. This matches native iOS/Android bottom-sheet behavior where backdrop tap is optional and swipe-down is primary.

- **PushNotificationHandler DI change**: Adding `UserRepository` changes the constructor signature and requires updating Wire providers. Low risk — follows the exact pattern of existing handlers.

- **Bottom-sheet consumer impact**: All consumers bind via `open`, `dismissable`, `sheet-closed`, and `au-slot`. None of these change. The internal DOM restructuring is transparent to consumers.
