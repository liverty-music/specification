# Tasks: semantic-html-landmarks

## 1. Add `<main>` landmark to route pages

- [x] 1.1 about-page.html: `<div class="about-card">` → `<main class="[ about-card ]">`
- [x] 1.2 auth-callback.html: `<div class="callback-layout">` → `<main class="[ callback-layout ]">`
- [x] 1.3 not-found-page.html: `<div class="not-found-layout">` → `<main class="[ not-found-layout ]">`
- [x] 1.4 welcome-page.html: `<div class="welcome-layout">` → `<main class="[ welcome-layout ]">`
- [x] 1.5 dashboard.html: `<div class="dashboard-layout">` → `<main class="[ dashboard-layout ]">`
- [x] 1.6 loading-sequence.html: `<div class="loading-layout">` → `<main class="[ loading-layout ]">`
- [x] 1.7 discover-page.html: `<div class="discover-layout">` → `<main class="[ discover-layout ]">`
- [x] 1.8 tickets-page.html: `<div class="page-layout">` → `<main class="[ page-layout ]">`
- [x] 1.9 settings-page.html: `<div class="settings-layout">` → `<main class="[ settings-layout ]">`
- [x] 1.10 my-artists-page.html: `<div class="page-layout">` → `<main class="[ page-layout ]">`

## 2. Replace div with semantic elements

- [x] 2.1 event-card.html: `<div>` → `<article>`, add `role="button" tabindex="0"` for clickable card
- [x] 2.2 signup-prompt-banner.html: `<div>` → `<aside>` with `aria-label`
- [x] 2.3 event-detail-sheet.html: wrap dates in `<time datetime=...>`, venue in `<address>`
- [x] 2.4 settings-page.html: `<div class="settings-divider">` → `<hr>` (4 instances)
- [x] 2.5 my-artists-page.html: `.page-header` div → `<header>`
- [x] 2.6 dashboard.html: `.dashboard-stale-banner` → `<aside>`
- [x] 2.7 live-highway.html: `.stage-header` → `<header>`, `.date-separator` → `<header>` or `<time>`
- [x] 2.8 welcome-page.html: wrap brand/hero area in `<header>`
- [x] 2.9 auth-status.html: outer `<div>` → `<nav>` or `<header>` with `aria-label`

## 3. Add ARIA attributes

- [x] 3.1 error-banner.html: add `aria-labelledby` to `<dialog>`
- [x] 3.2 user-home-selector.html: already has `t="[aria-label]userHome.title"` — no change needed
- [x] 3.3 my-artists-page.html: add `aria-label` to context menu `<dialog>`
- [x] 3.4 notification-prompt.html: add `aria-live="polite"` to state containers
- [x] 3.5 celebration-overlay.html: add `role="status" aria-live="polite"`
- [x] 3.6 loading-sequence.html: add `aria-label` to step dots container
- [x] 3.7 coach-mark.html: add `aria-label` to tooltip
- [x] 3.8 tickets-page.html: add `aria-labelledby` to generating dialog

## 4. Apply CUBE CSS bracket notation

- [x] 4.1 Apply brackets to all route page templates (10 files)
- [x] 4.2 Apply brackets to all component templates (18 files)

## 5. Verification

- [x] 5.1 `make lint` passes
- [x] 5.2 `make test` passes
- [x] 5.3 Block-level classes use CUBE CSS brackets (grep verified)
- [x] 5.4 All `<dialog>` elements have `aria-labelledby` or `aria-label`
- [x] 5.5 All route pages have `<main>` landmark
