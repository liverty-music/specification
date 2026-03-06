## Why

The app shell layout uses `position: fixed` + Popover API hacks to position the bottom navigation bar, causing the nav to render at the top of the viewport instead of the bottom due to UA stylesheet conflicts with the top layer. Additionally, the onboarding home selector can be dismissed by tapping outside the dialog during a mandatory step, and several CSS anti-patterns (physical properties, `100vh`) remain throughout the codebase despite the modern-css-platform spec requiring logical properties and dynamic viewport units.

## What Changes

- Replace the `position: fixed` + `popover="manual"` bottom navigation with a **CSS Grid app shell layout** (`grid-template-rows: 1fr min-content; height: 100dvh`) so the nav is an in-flow grid child at the bottom
- Remove per-page height hacks (`h-screen`, `pb-14`) that compensated for the fixed-position nav
- Add a `required` bindable to `user-home-selector` to prevent backdrop/ESC dismissal during onboarding
- Migrate all Tailwind physical directional classes (`ml-`, `mr-`, `pl-`, `pr-`, `left-`, `right-`) to logical equivalents (`ms-`, `me-`, `ps-`, `pe-`, `start-`, `end-`)
- Replace `100vh` with `100dvh` in all CSS files

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `app-shell-layout`: The app shell structure changes from `min-h-screen` + fixed nav to CSS Grid with `1fr min-content` rows. Nav is no longer in the top layer. Pages no longer need to account for nav bar height.
- `modern-css-platform`: Enforce logical property compliance in Tailwind HTML templates (previously only CSS files were covered). Fix remaining `100vh` instances.
- `frontend-onboarding-flow`: The home selector dialog becomes non-dismissible (no backdrop tap, no ESC) when opened during onboarding Step 3.
- `user-home`: The `user-home-selector` component gains a `required` bindable that prevents close-on-backdrop and close-on-ESC behavior.

## Impact

- **Frontend repo only** — no backend or specification changes
- **Files affected**:
  - `src/my-app.html` — Grid shell layout
  - `src/components/bottom-nav-bar/bottom-nav-bar.html` + `.ts` — Remove popover/fixed
  - `src/components/user-home-selector/user-home-selector.ts` + `.html` — Add `required` bindable
  - `src/routes/dashboard.html` + `.ts` — Remove `h-screen pb-14`, pass `required` to selector
  - `src/routes/discover/discover-page.css` — `100vh` to `100dvh`
  - `src/routes/onboarding-loading/loading-sequence.css` — `100vh` to `100dvh`
  - `src/routes/settings/settings-page.html` — Physical to logical Tailwind classes
  - `src/routes/my-artists/my-artists-page.html` — Physical to logical Tailwind classes
  - `src/components/toast-notification/toast-notification.html` — Physical to logical Tailwind classes
  - `src/components/live-highway/event-card.html` — Physical to logical Tailwind classes
- **No breaking API changes** — purely presentational fixes
