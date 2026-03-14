# Tasks: flatten-dom-structure

## 1. Remove unnecessary wrapper divs

- [ ] 1.1 auth-callback.html/.css: remove `.callback-content` wrapper, merge styles into parent
- [ ] 1.2 welcome-page.html/.css: remove `.welcome-content` wrapper
- [ ] 1.3 dashboard.html/.css: flatten `.dashboard-stale-banner` > `.dashboard-stale-content`
- [ ] 1.4 tickets-page.html/.css: flatten `.state-center` > `.state-content` (3 instances)
- [ ] 1.5 my-artists-page.html/.css: flatten `.state-center` > `.state-content`
- [ ] 1.6 notification-prompt.html/.css: flatten `.prompt-row` > `.prompt-body` nesting
- [ ] 1.7 pwa-install-prompt.html/.css: evaluate `.prompt-icon-wrap` removal

## 2. Replace overlay divs with CSS pseudo-elements

- [ ] 2.1 my-artists-page.css: replace `.grid-tile-overlay` div with `.grid-tile::before` pseudo-element
- [ ] 2.2 my-artists-page.html: remove `.grid-tile-overlay` element

## 3. Simplify coach-mark structure

- [ ] 3.1 coach-mark.html/.css: consolidate 4 `.click-blocker` divs into single element with CSS clip-path or mask
- [ ] 3.2 coach-mark.html/.css: merge 2 arrow SVGs into 1 with CSS transform for direction

## 4. Flatten bottom-nav-bar

- [ ] 4.1 bottom-nav-bar.html/.css: remove `.nav-bar-inner` wrapper

## 5. Update tests

- [ ] 5.1 Update test selectors that reference removed wrapper elements
- [ ] 5.2 Update E2E assertions if any target flattened structures

## 6. Verification

- [ ] 6.1 `make lint` passes
- [ ] 6.2 `make test` passes
- [ ] 6.3 Visual comparison: no layout changes visible
