## 1. Foundation — styles/ infrastructure (PR 1)

- [x] 1.1 Create `src/styles/tokens.css` — extract `@theme` block from `my-app.css` into plain CSS custom properties on `:root` (colors, typography, radii, shadows, container breakpoints, transition tokens, spacing scale)
- [x] 1.2 Create `src/styles/reset.css` — write custom CSS reset using `:where()` selectors inside `@layer reset`
- [x] 1.3 Create `src/styles/global.css` — write base element styles inside `@layer global` (body, h1-h6 fluid typography, a, button, input, svg defaults, view transition styles, dark theme defaults)
- [x] 1.4 Create `src/styles/compositions.css` — define initial composition primitives inside `@layer composition` (.stack, .cluster, .center, .wrapper, .grid-auto)
- [x] 1.5 Create `src/styles/utilities.css` — move `@keyframes` and `.animate-*` classes from `my-app.css` inside `@layer utility`, add `prefers-reduced-motion` override
- [x] 1.6 Create `src/styles/main.css` — `@layer` order declaration + `@import` statements in correct order
- [x] 1.7 Update `main.ts` to `import './styles/main.css'`
- [x] 1.8 Verify Tailwind and CUBE CSS co-exist — `npm run build` succeeds, no visual regressions on dev server

## 2. App shell migration (PR 2)

- [x] 2.1 Rewrite `my-app.css` — wrap app shell layout (my-app, main, au-viewport, live-highway, overlay collapse) in `@layer block { @scope(my-app) { ... } }`
- [x] 2.2 Move `.event-card-responsive` container query rules from `my-app.css` to `event-card.css`
- [x] 2.3 Remove `@import "tailwindcss"` and `@theme` block from `my-app.css`
- [x] 2.4 Verify `npm run build` succeeds and app shell layout is intact

## 3. Small component migration (PR 3)

- [x] 3.1 Migrate `dna-orb-canvas.css` — wrap in `@layer block { @scope(dna-orb-canvas) {} }`
- [x] 3.2 Migrate `dna-orb-canvas.html` — remove any Tailwind classes
- [x] 3.3 Migrate `error-banner.css` — wrap in `@layer block { @scope(error-banner) {} }`
- [x] 3.4 Migrate `error-banner.html` — replace Tailwind classes with block CSS + compositions
- [x] 3.5 Migrate `tickets-page.css` — wrap in `@layer block { @scope(tickets-page) {} }`
- [x] 3.6 Migrate `tickets-page.html` — replace Tailwind classes with block CSS + compositions

## 4. Medium component migration (PR 4)

- [x] 4.1 Migrate `toast-notification.css` + `.html` — block-scope CSS, remove Tailwind from HTML
- [x] 4.2 Migrate `signup-modal.css` + `.html` — block-scope CSS, remove Tailwind from HTML
- [x] 4.3 Migrate `event-detail-sheet.css` + `.html` — block-scope CSS, remove Tailwind from HTML
- [x] 4.4 Migrate `user-home-selector.css` + `.html` — block-scope CSS, remove Tailwind from HTML
- [x] 4.5 Migrate `my-artists-page.css` + `.html` — block-scope CSS, remove Tailwind from HTML

## 5. Large component migration (PR 5-6)

- [x] 5.1 Migrate `event-card.css` + `.html` — block-scope CSS, absorb `.event-card-responsive` rules, remove Tailwind from HTML
- [x] 5.2 Migrate `coach-mark.css` + `.html` — block-scope CSS, fix `container-name` warning, fix `vw` → `vi` warning, fix property order warning
- [x] 5.3 Migrate `loading-sequence.css` + `.html` — block-scope CSS, fix `container-name` warnings, remove Tailwind from HTML
- [x] 5.4 Migrate `celebration-overlay.css` + `.html` — block-scope CSS, remove Tailwind from HTML
- [x] 5.5 Migrate `discover-page.css` + `.html` — block-scope CSS, fix `container-name` warnings, remove Tailwind from HTML (largest file: 416 lines, may need extraction to compositions)

## 6. Remaining HTML template migration (PR 7)

- [x] 6.1 Migrate `welcome-page.html` — replace Tailwind classes (heavy animation + gradient usage)
- [x] 6.2 Migrate `bottom-nav-bar.html` — replace Tailwind classes
- [x] 6.3 Migrate `auth-status.html` — replace Tailwind classes
- [x] 6.4 Migrate `auth-callback.html` — replace Tailwind classes
- [x] 6.5 Migrate `dashboard.html` — replace Tailwind classes
- [x] 6.6 Migrate `not-found-page.html` — replace Tailwind classes
- [x] 6.7 Migrate `settings-page.html` — replace Tailwind classes
- [x] 6.8 Migrate `notification-prompt.html` — replace Tailwind classes
- [x] 6.9 Migrate `pwa-install-prompt.html` — replace Tailwind classes
- [x] 6.10 Migrate `inline-error.html` — replace Tailwind classes
- [x] 6.11 Migrate `about-page.html` — replace Tailwind classes
- [x] 6.12 Migrate `live-highway.html` — replace Tailwind classes

## 7. Tailwind removal and cleanup (PR 8)

- [x] 7.1 Remove `@tailwindcss/vite` from `vite.config.ts`
- [x] 7.2 Remove `tailwindcss` and `@tailwindcss/vite` from `package.json`
- [x] 7.3 Run `npm install` to clean lockfile
- [x] 7.4 Update `AGENTS.md` — change stack table from TailwindCSS to CUBE CSS
- [x] 7.5 Update stylelint rules from warnings to errors (promote `cube/*` rules)
- [x] 7.6 Verify `npm run lint:css` reports 0 warnings and 0 errors
- [x] 7.7 Verify `npm run build` succeeds
- [x] 7.8 Full visual regression check on dev server across all routes
