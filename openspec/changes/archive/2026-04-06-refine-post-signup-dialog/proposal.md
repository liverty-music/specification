## Why

The PostSignupDialog can appear nearly empty — showing only the title and a "Later" button — when the user has already installed the PWA and notification permission is already granted. This leaves users confused about what "Later" refers to and makes the app feel broken.

## What Changes

- Add a permanently visible hype guide hint row explaining that users can control notification scope via hype settings on the My Artists page
- Change the footer button label from "Later" to "Close" when both PWA installation and push notification opt-in are already complete

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `post-signup-dialog`: Add always-visible hype guide row and dynamic footer button label ("Later" → "Close") based on completion state of PWA install and push notification opt-in

## Impact

- `frontend/src/components/post-signup-dialog/post-signup-dialog.html` — template changes
- `frontend/src/components/post-signup-dialog/post-signup-dialog.ts` — new `isAllDone` computed getter
- `frontend/src/locales/en/translation.json` — new `postSignup.hypeGuideLabel` and `postSignup.close` keys
- `frontend/src/locales/ja/translation.json` — same new keys in Japanese
