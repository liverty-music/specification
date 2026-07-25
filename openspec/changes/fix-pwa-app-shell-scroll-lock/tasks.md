## 1. Confirm current structure

- [ ] 1.1 Confirm `app-shell.css` remains the single height owner (`block-size: 100dvh` grid); no change needed
- [ ] 1.2 Identify the canonical inner scroll container in the current tree (`.concert-scroll` vs the live-highway variant) that must receive `overscroll-behavior: contain`

## 2. Root scroll lock (reset.css)

- [ ] 2.1 Add a root rule to `src/styles/reset.css`: `html, body { block-size: 100%; overflow: hidden; overscroll-behavior: none; }`
- [ ] 2.2 Remove `body { min-block-size: 100dvh }` from `src/styles/reset.css`
- [ ] 2.3 Verify no route relies on document-level scroll (all routes delegate scrolling to inner containers)

## 3. Inner scroller containment

- [ ] 3.1 Add `overscroll-behavior: contain` to the concert scroll container (`.concert-scroll`)

## 4. Tests

- [ ] 4.1 Extend the layout/shell E2E (or `layout-assertions`) suite: in a standalone-emulated viewport on the dashboard, assert the bottom nav bar and header stay pinned after a downward overscroll gesture, and the document root does not scroll
- [ ] 4.2 Run `make check` (Biome + stylelint + typecheck + unit tests) and confirm green

## 5. Ship to production

- [ ] 5.1 Open the frontend PR, get CI green, and merge
- [ ] 5.2 Cut a frontend GitHub Release (SemVer tag) → automated pin-bump → ArgoCD auto-sync to prod
- [ ] 5.3 Verify on the installed prod PWA (Android Chrome home-screen and iOS home-screen): pull-to-refresh no longer hides the bottom nav or the header
- [ ] 5.4 Archive the OpenSpec change once verified in prod
