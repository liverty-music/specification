## 1. Fix overlay element flow

- [x] 1.1 In `src/my-app.css`, change the overlay element rule (`pwa-install-prompt, notification-prompt, toast-notification, error-banner`) from `overflow: hidden; display: block; block-size: 0` to `position: fixed` with flow-removal properties, and add `coach-mark` to the selector list
- [x] 1.2 Ensure overlay elements don't intercept pointer events (add `pointer-events: none` if not already handled by top-layer)

## 2. Verify

- [x] 2.1 Run `make check` to confirm lint + tests pass
- [x] 2.2 Visual verification in DevTools mobile view: bottom-nav-bar stays pinned at viewport bottom
- [x] 2.3 Visual verification in DevTools mobile view: stage header remains sticky when scrolling the event list
