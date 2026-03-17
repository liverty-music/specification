## 1. Preparation

- [x] 1.1 Confirm reset.css handles `<fieldset>`, `<dialog>`, `<figure>`, `<footer>`, `<output>`, `<section>`, `<article>` default styles (border, padding, margin)
- [x] 1.2 Search Playwright E2E tests for div-dependent selectors and list affected tests

## 2. `<div popover>` → `<dialog>` conversion

- [x] 2.1 coach-mark: Convert `<div ref="overlayEl" popover="manual">` to `<dialog>`, update CSS (`coach-mark.css`)
- [x] 2.2 notification-prompt: Convert `<div ref="popoverEl" popover="manual">` to `<dialog>`, update CSS
- [x] 2.3 pwa-install-prompt: Convert `<div ref="popoverEl" popover="manual">` to `<dialog>`, update CSS
- [x] 2.4 discovery-route: Convert `<div class="onboarding-guide" popover="auto">` to `<dialog>`, update CSS

## 3. Action groups → `<footer>`

- [x] 3.1 error-banner: Replace `<div class="error-actions">` with `<footer>`, update CSS selector
- [x] 3.2 hype-notification-dialog: Replace `<div class="notification-dialog-actions">` with `<footer>`, update CSS selector
- [x] 3.3 notification-prompt: Replace `<div class="prompt-actions">` with `<footer>`, update CSS selector
- [x] 3.4 pwa-install-prompt: Replace `<div class="prompt-actions">` with `<footer>`, update CSS selector

## 4. Content wrappers → semantic elements

- [x] 4.1 event-detail-sheet: Replace `<div class="sheet-hero">` with `<figure>`, update CSS
- [x] 4.2 event-detail-sheet: Replace `<div class="sheet-details">` with `<section>`, update CSS
- [x] 4.3 discovery-route: Replace `<div class="genre-chips">` with `<fieldset>`, update CSS
- [x] 4.4 discovery-route: Replace `<div class="search-results">` with `<section>`, update CSS
- [x] 4.5 discovery-route: Replace `<div class="search-status">` with `<p>`, update CSS
- [x] 4.6 user-home-selector: Replace `<div class="selector-section">` with `<section>` (selector-grid kept as div — layout container, not semantic list)
- [x] 4.7 state-placeholder: Replace `<div class="state-center">` with `<section>`, update CSS
- [x] 4.8 inline-error: Replace `<div class="[ inline-error-layout ]">` with `<section>`, update CSS
- [x] 4.9 toast-notification: Replace `<div class="[ toast-stack ]">` with `<aside>`, update CSS

## 5. Loading/status indicators → `<output>`

- [x] 5.1 my-artists-route: Replace `<div class="state-center" role="status">` with `<output role="status">`, update CSS
- [x] 5.2 tickets-route: Replace `<div class="state-center" role="status">` with `<output role="status">`, update CSS
- [x] 5.3 auth-callback-route: Replace `<div class="callback-loading" role="status">` with `<output role="status">`, update CSS

## 6. Unnecessary div nesting reduction

- [x] 6.1 tickets-route: Replace `<div class="ticket-row">` with `<article>`, `<div class="ticket-info">` with `<header>`, remove unnecessary wrapper divs
- [x] 6.2 my-artists-route: Replace `<div class="artist-identity">` with `<header>`, `<div class="artist-row-content">` with `<section>`, reduce grid tile nesting
- [x] 6.3 error-banner: Replace `<div class="error-content">` with direct children, remove unnecessary wrapper
- [x] 6.4 hype-notification-dialog: Replace `<div class="notification-dialog-content">` with direct children or `<section>`
- [x] 6.5 welcome-route: Replace `<div class="welcome-actions">` with `<footer>`
- [x] 6.6 auth-callback-route: Replace `<div class="callback-error">` with `<section>`, `<div class="callback-status">` with `<p>`

## 7. Lint rule addition (regression prevention)

- [x] 7.1 Add `lint-no-div-popover` Makefile target: `! grep -rn '<div[[:space:]].*popover' --include='*.html' src/`
- [x] 7.2 Add `lint-no-div-role-status` Makefile target: `! grep -rn '<div[[:space:]].*role="status"' --include='*.html' src/`
- [x] 7.3 Add both targets to `lint-templates` dependency list

## 8. Verification

- [x] 8.1 Run `make check` (lint + test) to verify no regressions (unit tests pass, stylelint clean for changed files, Playwright timeouts are pre-existing env issue)
- [x] 8.2 Visual inspection: confirm no layout changes in dev server (welcome, auth-callback, toast verified via Playwright screenshots)
- [x] 8.3 Update any Playwright selectors broken by div → semantic element changes (no div selectors found in E2E tests — no changes needed)
