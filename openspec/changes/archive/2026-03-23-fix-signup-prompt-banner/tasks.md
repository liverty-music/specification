## 1. Fix banner visual style

- [x] 1.1 Replace `--_surface-bg` with frosted glass background (`oklch(18% 0.04 275deg / 85%)` + `backdrop-filter: blur(12px)`) in `signup-prompt-banner.css`
- [x] 1.2 Replace top border with 2px gradient (`--color-brand-primary` → `--color-brand-secondary`) using `border-image` or pseudo-element
- [x] 1.3 Add `@keyframes cta-glow` animation on `.signup-banner-btn` (box-shadow pulse, 2.5s cycle, ease-in-out)
- [x] 1.4 Add `@keyframes banner-enter` slide-in animation on `:scope` (translateY + opacity, 400ms ease-out)
- [x] 1.5 Wrap both animations in `@media (prefers-reduced-motion: no-preference)`

## 2. Fix banner display on My Artists

- [x] 2.1 Add `showSignupBanner = true` logic in `my-artists-route.ts` `loading()` when `!authService.isAuthenticated && onboarding.isCompleted`

## 3. Fix 401 error on Dashboard

- [x] 3.1 Inject `IAuthService` into `DashboardService` constructor
- [x] 3.2 Add `isAuthenticated` guard in `fetchJourneyMap()` — return `new Map()` for unauthenticated users

## 4. Verify

- [x] 4.1 Run `make check` in frontend repo
