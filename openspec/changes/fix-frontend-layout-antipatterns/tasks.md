## 1. CSS Grid App Shell

- [ ] 1.1 Replace `my-app.html` root div: change `min-h-screen` to `grid grid-rows-[1fr_min-content] h-dvh`, move prompts inside `<main>`, add `overflow-y-auto` to `<main>`
- [ ] 1.2 Remove `popover="manual"` attribute and `fixed inset-x-0 bottom-0` classes from `bottom-nav-bar.html`; replace with simple flow-based nav styling
- [ ] 1.3 Remove `showPopover()` call and `navElement` ref from `bottom-nav-bar.ts`
- [ ] 1.4 Remove `h-screen pb-14` from `dashboard.html` and any other route templates that compensate for fixed nav height

## 2. Home Selector Required Mode

- [ ] 2.1 Add `@bindable required = false` to `user-home-selector.ts`
- [ ] 2.2 Update `handleBackdropClick` to return early when `required` is `true`
- [ ] 2.3 Update `handleCancel` to only call `close()` when `required` is `false` (keep `preventDefault()` always)
- [ ] 2.4 Add `required.bind="isOnboarding"` to `<user-home-selector>` in `dashboard.html`

## 3. Physical to Logical Tailwind Classes

- [ ] 3.1 Migrate `settings-page.html`: `ml-8` to `ms-8`, `left-0.5` to `start-0.5`
- [ ] 3.2 Migrate `my-artists-page.html`: `ml-4` to `ms-4`, `right-0` to `end-0`, `left-4` to `start-4`, `right-4` to `end-4`
- [ ] 3.3 Migrate `toast-notification.html`: `left-0 right-0` to `start-0 end-0`
- [ ] 3.4 Migrate `event-card.html`: `right-2` to `end-2`, `right-1.5` to `end-1.5`

## 4. Dynamic Viewport Height

- [ ] 4.1 Replace `100vh` with `100dvh` in `discover-page.css`
- [ ] 4.2 Replace `100vh` with `100dvh` in `loading-sequence.css`

## 5. Verification

- [ ] 5.1 Run `make check` (lint + test) and fix any failures
- [ ] 5.2 Visually verify bottom nav renders at the bottom of the viewport
- [ ] 5.3 Visually verify home selector cannot be dismissed during onboarding Step 3
