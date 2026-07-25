## Why

In the installed (standalone) PWA, a pull-to-refresh / overscroll gesture makes the whole document scroll: the bottom navigation bar drops off-screen, and scrolling the dashboard to the bottom brings the nav back but pushes the header (the "Timetable" title row) off the top. The root cause is that the document root (`html`/`body`) is allowed to be a scroll source — there is no root scroll lock and no `overscroll-behavior`, so the native pull-to-refresh gesture shifts the fixed shell chrome. This is the classic PWA app-shell "the whole document scrolls" bug and it degrades core navigation on the primary install target (mobile home-screen PWA).

## What Changes

- Lock the document root as a non-scrolling frame: `html`/`body` get a definite height, `overflow: hidden`, and `overscroll-behavior: none` so the document is never a scroll source and the standalone pull-to-refresh gesture cannot shift the shell.
- Remove `body { min-block-size: 100dvh }` — with the `app-shell` grid owning height (`100dvh`), the `min-block-size` on `body` is a redundant scroll source that `dvh` fluctuation can push past the visible viewport.
- Add `overscroll-behavior: contain` to the single inner scroll container (the concert list scroller) so reaching a scroll boundary never chains into the document.
- Keep the existing standard-conformant parts unchanged: the `100dvh` grid shell, `viewport-fit=cover`, and `env(safe-area-inset-*)` handling remain as-is.

## Capabilities

### New Capabilities
<!-- None: this is a bug fix to existing shell layout behavior. -->

### Modified Capabilities
- `shell-layout`: Add a requirement that the document root is a non-scrolling frame (root scroll lock + `overscroll-behavior` neutralization), and strengthen the bottom-nav-pinning requirement to hold under a standalone PWA pull-to-refresh / overscroll gesture, with scroll confined to the single inner container.

## Impact

- Affected code (frontend):
  - `src/styles/reset.css` — root scroll lock on `html`/`body`; remove `body { min-block-size: 100dvh }`.
  - `src/app-shell.css` — shell grid height unchanged (`100dvh`); verify it remains the height owner.
  - The inner concert scroll container (`.concert-scroll`) — add `overscroll-behavior: contain`.
- No proto/BSR, backend, or API changes. Frontend-only CSS change.
- Testing: extend the existing layout/shell E2E assertions to cover nav-pinned-after-overscroll in a standalone-emulated viewport.
- Risk: root `overflow: hidden` disables native pull-to-refresh reload in the browser tab; acceptable because the app is designed as an installed PWA and provides its own data-refresh paths.
