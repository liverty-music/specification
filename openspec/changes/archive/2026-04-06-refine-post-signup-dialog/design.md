## Context

The `PostSignupDialog` is a bottom sheet shown once after a user's first signup. It consolidates PWA install and push notification opt-in prompts. However, when both are already satisfied (PWA installed via standalone mode, notification permission already granted), the sheet renders with only the title and an unexplained "Later" button, which feels broken and confusing.

Additionally, users currently have no in-context guidance about hype — the mechanism for controlling notification granularity per artist. The dialog is a natural moment to introduce this concept.

## Goals / Non-Goals

**Goals:**
- Always show a hype guide hint row so the sheet always has meaningful content
- Dynamically change the footer button to "Close" (vs "Later") when no pending actions remain
- Avoid sheet suppression logic — always show the sheet after first signup regardless of state

**Non-Goals:**
- Navigation to My Artists from within the dialog
- Changing when or how often the sheet appears
- Modifying notification or PWA install logic

## Decisions

### Always-visible hype guide row

The hype guide row is added as a static, non-interactive informational row. It requires no condition because:
- It is always relevant regardless of notification or PWA state
- It ensures the sheet never appears empty
- It introduces the hype concept at the ideal moment (right after signup)

**Alternative considered**: Show the row only if notification is granted (user can now act on it). Rejected because it would still leave the sheet empty for users with notification denied + PWA installed.

### `isAllDone` computed getter for button label

A getter `isAllDone` is introduced in the ViewModel:

```
isAllDone = !canInstallPwa && notificationManager.permission === 'granted'
```

- `!canInstallPwa`: true when PWA is already installed (standalone mode) or install is not applicable
- `permission === 'granted'`: user has opted into push notifications

When both are true, the footer button uses the `postSignup.close` i18n key; otherwise `postSignup.defer`.

**Binding approach**: Use `t.bind` (Aurelia i18n dynamic key binding) rather than template literal `t="${...}"`, which is not supported by the `@aurelia/i18n` attribute.

### No structural changes to sheet dismissal

Both "Later" and "Close" call `onDefer()`, which sets `isOpen = false`. No behavioral difference — only the label changes to communicate intent accurately.

## Risks / Trade-offs

- [Resolved] `isAllDone` reactivity depends on `notificationManager.permission` being observable. `NotificationManager.permission` is decorated with `@observable` (notification-manager.ts:13), so Aurelia will automatically re-evaluate `isAllDone` and update the footer button label when permission changes mid-session.
- [Trade-off] Hype guide row has no CTA (no navigation button). Users must find My Artists themselves. → Acceptable for MVP; a navigation link can be added in a follow-up if metrics show confusion.
