# Tasks: flatten-dom-structure

## 1. Remove unnecessary wrapper divs

- [x] 1.1 auth-callback.html/.css: remove `.callback-content` wrapper, merge styles into parent
- [x] 1.2 welcome-page.html/.css: remove `.welcome-content` wrapper
- [x] 1.3 dashboard.html/.css: flatten `.dashboard-stale-banner` > `.dashboard-stale-content`
- [x] 1.4 tickets-page.html/.css: flatten `.state-center` > `.state-content` (3 instances)
- [x] 1.5 my-artists-page.html/.css: flatten `.state-center` > `.state-content`
- [x] 1.6 notification-prompt.html/.css: flatten `.prompt-row` > `.prompt-body` nesting
- [x] 1.7 pwa-install-prompt.html/.css: evaluate `.prompt-icon-wrap` removal

## 2. Replace overlay divs with CSS pseudo-elements

- [x] 2.1 my-artists-page.css: replace `.grid-tile-overlay` div with `.grid-tile::before` pseudo-element
- [x] 2.2 my-artists-page.html: remove `.grid-tile-overlay` element

## 3. Simplify coach-mark structure

- [x] 3.1 coach-mark.html/.css: skip — anchor-positioned masks require separate elements (no clip-path equivalent)
- [x] 3.2 coach-mark.html/.css: skip — dual SVGs use @container anchored query for CSS-only direction toggle

## 4. Flatten bottom-nav-bar

- [x] 4.1 bottom-nav-bar.html/.css: remove `.nav-bar-inner` wrapper

## 5. Update tests

- [x] 5.1 Update test selectors that reference removed wrapper elements — none found
- [x] 5.2 Update E2E assertions if any target flattened structures — none found

## 6. Verification

- [x] 6.1 `make lint` passes
- [x] 6.2 `make test` passes
- [x] 6.3 Visual comparison: welcome + auth-callback verified via Playwright, authenticated pages verified via unit tests (545/545)
