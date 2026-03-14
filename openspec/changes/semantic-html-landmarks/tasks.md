# Tasks: semantic-html-landmarks

## 1. Add `<main>` landmark to route pages

- [ ] 1.1 about-page.html: `<div class="about-card">` → `<main class="[ about-card ]">`
- [ ] 1.2 auth-callback.html: `<div class="callback-layout">` → `<main class="[ callback-layout ]">`
- [ ] 1.3 not-found-page.html: `<div class="not-found-layout">` → `<main class="[ not-found-layout ]">`
- [ ] 1.4 welcome-page.html: `<div class="welcome-layout">` → `<main class="[ welcome-layout ]">`
- [ ] 1.5 dashboard.html: `<div class="dashboard-layout">` → `<main class="[ dashboard-layout ]">`
- [ ] 1.6 loading-sequence.html: `<div class="loading-layout">` → `<main class="[ loading-layout ]">`
- [ ] 1.7 discover-page.html: `<div class="discover-layout">` → `<main class="[ discover-layout ]">`
- [ ] 1.8 tickets-page.html: `<div class="page-layout">` → `<main class="[ page-layout ]">`
- [ ] 1.9 settings-page.html: `<div class="settings-layout">` → `<main class="[ settings-layout ]">`
- [ ] 1.10 my-artists-page.html: `<div class="page-layout">` → `<main class="[ page-layout ]">`

## 2. Replace div with semantic elements

- [ ] 2.1 event-card.html: `<div>` → `<article>`, add `role="button" tabindex="0"` for clickable card
- [ ] 2.2 signup-prompt-banner.html: `<div>` → `<aside>` with `aria-label`
- [ ] 2.3 event-detail-sheet.html: wrap dates in `<time datetime=...>`, venue in `<address>`
- [ ] 2.4 settings-page.html: `<div class="settings-divider">` → `<hr>` (3 instances)
- [ ] 2.5 my-artists-page.html: `.page-header` div → `<header>`
- [ ] 2.6 dashboard.html: `.dashboard-stale-banner` → `<aside>`
- [ ] 2.7 live-highway.html: `.stage-header` → `<header>`, `.date-separator` → `<header>` or `<time>`
- [ ] 2.8 welcome-page.html: wrap brand/hero area in `<header>`
- [ ] 2.9 auth-status.html: outer `<div>` → `<nav>` or `<header>` with `aria-label`

## 3. Add ARIA attributes

- [ ] 3.1 error-banner.html: add `aria-labelledby` to `<dialog>`
- [ ] 3.2 user-home-selector.html: add `aria-labelledby` to `<dialog>`
- [ ] 3.3 my-artists-page.html: add `aria-label` to context menu `<dialog>`
- [ ] 3.4 notification-prompt.html: add `aria-live="polite"` to state containers
- [ ] 3.5 celebration-overlay.html: add `role="status" aria-live="polite"`
- [ ] 3.6 loading-sequence.html: add `aria-label` to step dots container
- [ ] 3.7 coach-mark.html: add `aria-label` to tooltip
- [ ] 3.8 tickets-page.html: add `aria-labelledby` to generating dialog

## 4. Apply CUBE CSS bracket notation

- [ ] 4.1 Apply brackets to all route page templates (10 files)
- [ ] 4.2 Apply brackets to all component templates (18 files)

## 5. Verification

- [ ] 5.1 `make lint` passes
- [ ] 5.2 `make test` passes
- [ ] 5.3 No `class="[^[]` patterns without brackets remain (grep check)
- [ ] 5.4 All `<dialog>` elements have `aria-labelledby` or `aria-label`
- [ ] 5.5 All route pages have `<main>` landmark
