## 1. Design System Foundation

- [x] 1.1 Define design tokens in `my-app.css` using Tailwind v4 `@theme` directive (color palette, surface colors, text colors, radius, shadow tokens)
- [x] 1.2 Add display font (Outfit) via Google Fonts — preconnect and stylesheet link in `index.html`, define `--font-display` token
- [x] 1.3 Remove legacy scaffold CSS from `my-app.css` (`nav { background: #eee }`, raw `a` styles)
- [x] 1.4 Update `index.html` — set `<title>Liverty Music</title>`, add favicon link, add font preload

## 2. App Shell Layout

- [x] 2.1 Redesign `my-app.html` — conditional nav visibility (hide during onboarding routes, show on dashboard)
- [x] 2.2 Restyle `my-app.html` nav bar with dark theme using design system tokens
- [x] 2.3 Redesign `auth-status.html` — unified color scheme, remove red/green/blue button mix, use brand accent colors
- [x] 2.4 Implement page transition animation — wrap `<au-viewport>` in transition container, add CSS fade+slide transitions
- [x] 2.5 Add `prefers-reduced-motion` media query to disable transitions for users who prefer it

## 3. Landing Page Refinement

- [x] 3.1 Redesign `welcome-page.html` — dark gradient background, display font for hero copy, brand logo/wordmark above hero
- [x] 3.2 Restyle CTA buttons — primary Sign Up with brand accent glow, secondary Sign In with ghost/outline style
- [x] 3.3 Add hero entrance animation — staggered fade-in for heading, sub-heading, and CTA button

## 4. Artist Discovery Visual Enhancement

- [x] 4.1 Update `dna-orb-canvas.ts` bubble rendering — per-artist color differentiation using HSL hash (replace uniform purple gradient)
- [x] 4.2 Add background visual depth — subtle starfield or particle layer behind bubbles in `artist-discovery-page.css`
- [x] 4.3 Add onboarding guidance overlay — "Tap bubbles to follow artists" tooltip on first visit, auto-dismiss after first tap or 5 seconds
- [x] 4.4 Add orb label text — display "Music DNA" or follow count label near the DNA Orb
- [x] 4.5 Enhance toast notification design — vibrant accent background, spring/bounce entrance animation in `toast-notification.html`

## 5. Loading Sequence Enhancement

- [x] 5.1 Add visual progress indicator to `loading-sequence.html` — progress bar or step dots showing phase progression
- [x] 5.2 Add step indicator display — phase number (e.g., "1/3", "2/3", "3/3") or visual dots
- [x] 5.3 Add animated visual element — pulsing orb, particle animation, or animated gradient beyond text-only display
- [x] 5.4 Ensure visual continuity — verify background gradient matches Artist Discovery screen

## 6. Dashboard Polish

- [x] 6.1 Apply dark theme to `dashboard.html` and `live-highway.html` — dark surface backgrounds, light text
- [x] 6.2 Update `color-generator.ts` — adjust lightness range to 55-65% for adequate contrast on dark backgrounds
- [x] 6.3 Enlarge mega-typography in `event-card.html` main lane — increase to text-4xl+ using display font
- [x] 6.4 Add card visual depth — subtle gradient, shadow, or glow effect on main lane cards
- [x] 6.5 Style date separators — accent color text, dark surface background, improved typography weight
- [x] 6.6 Restyle dashboard header — "Live Highway" in display font with brand styling, dark background
- [x] 6.7 Add card entrance animation — subtle fade-in/slide-up as cards scroll into viewport (CSS-only with Intersection Observer)

## 7. Detail Sheet & Icons

- [x] 7.1 Create SVG icon components in `src/components/icons/` — calendar, map-pin, link icons using `currentColor`
- [x] 7.2 Replace Unicode emoji in `event-detail-sheet.html` with SVG icon components
- [x] 7.3 Restyle detail sheet buttons — brand accent color for primary action, dark-themed outline for secondary
- [x] 7.4 Add swipe-to-dismiss gesture to `event-detail-sheet.ts` — detect downward swipe to close sheet
- [x] 7.5 Apply dark theme to detail sheet — dark surface background, light text, brand accent header

## 8. Region Setup

- [x] 8.1 Create `region-setup-sheet` component — bottom sheet with prefecture dropdown/quick-select buttons
- [x] 8.2 Integrate region setup trigger in Dashboard — detect missing region, show blurred dashboard + overlay
- [x] 8.3 Implement region save — localStorage persistence (UserService.UpdateRegion RPC not yet available), close sheet, unblur dashboard
- [x] 8.4 Style region setup sheet — dark theme, design system tokens, smooth open/close animation

## 9. Bug Fix & Cleanup

- [x] 9.1 Fix `concert-service.ts` import error — change `import { transport }` to `import { createTransport }` to match `grpc-transport.ts` export
- [x] 9.2 Update `welcome-page.stories.ts` — reflect new dark theme and design for Storybook
