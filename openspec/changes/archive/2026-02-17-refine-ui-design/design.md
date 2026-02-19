## Context

The Liverty Music frontend is an Aurelia 2 SPA using Tailwind CSS v4, with a canvas-based Artist Discovery (Matter.js physics), a typography-focused Live Highway dashboard, and Zitadel authentication. The current implementation is functionally complete but visually at prototype quality — plain white backgrounds, scaffold page titles (`<title>Aurelia</title>`), raw CSS (`nav { background: #eee }`), inconsistent theming (dark for Bubble UI, white for everything else), and no brand identity.

A detailed UI analysis identified 50+ improvement points across all screens (see `docs/ui-design-analysis.md`). This design document establishes how to systematically address them.

**Current tech:**
- Aurelia 2 with `@aurelia/router`
- Tailwind CSS v4 (via `@tailwindcss/vite`)
- Matter.js for physics simulation
- Canvas 2D API for bubble/orb rendering
- ShadowDOM for some components (LoadingSequence, DnaOrbCanvas)

## Goals / Non-Goals

**Goals:**
- Establish a reusable design system via Tailwind v4 theme tokens
- Unify visual theme across all screens (dark-first)
- Bring all screens to production-quality visual polish
- Add micro-interactions and transitions for an engaging experience
- Fix critical issues: brand identity, CTA design, region setup flow
- Maintain performance budget (60fps on mobile for animated screens)

**Non-Goals:**
- Backend API changes (purely frontend visual refinement)
- New feature development (e.g., social sharing, ticket purchase)
- Redesigning the information architecture or navigation flow
- Adding new authentication providers beyond Passkey/Zitadel
- Sound effects or haptic feedback (deferred to post-MVP)
- Full accessibility audit (maintain existing a11y, improve incrementally)

## Decisions

### Decision 1: Dark-First Unified Theme

**Choice:** Dark theme as default for all screens.

**Rationale:** The Artist Discovery and Loading Sequence screens already use dark backgrounds (`rgb(3 7 18)` to `rgb(49 46 129)`). The music/entertainment domain strongly favors dark themes (Spotify, Apple Music, YouTube Music all use dark). Extending dark to Welcome and Dashboard provides visual continuity and brand coherence.

**Alternative considered:** Light theme everywhere — rejected because it conflicts with the existing canvas-based dark UI and doesn't match the music domain aesthetic.

**Implementation:**
- Define dark palette tokens in Tailwind `@theme` block
- Background: deep navy/indigo gradients (`gray-950` → `indigo-950`)
- Text: white/gray-200 primary, gray-400 secondary
- Accent: indigo-500 / violet-500 for interactive elements
- Card surfaces: gray-900/gray-800 with subtle opacity

### Decision 2: Tailwind v4 CSS-First Design Tokens

**Choice:** Use Tailwind v4's `@theme` directive in CSS (not `tailwind.config.ts`) for design tokens.

**Rationale:** Tailwind v4 is CSS-first. The project already uses `@import "tailwindcss"` in `my-app.css`. Defining tokens in CSS aligns with the v4 approach and avoids the config file overhead. Tokens propagate to all components using Tailwind utilities.

**Alternative considered:** JavaScript config file — rejected as v4 deprecated this pattern.

**Tokens to define:**
```
--color-brand-*     (primary, secondary, accent)
--color-surface-*   (background layers)
--color-text-*      (primary, secondary, muted)
--font-display      (headings: Inter/Outfit/etc.)
--font-body         (body: system-ui)
--radius-*          (card, button, sheet)
--shadow-*          (card-glow, sheet)
```

### Decision 3: Per-Screen CSS Approach

**Choice:** Keep ShadowDOM CSS for canvas-heavy components (DnaOrbCanvas, LoadingSequence), use Tailwind utility classes for all other components.

**Rationale:** Canvas components need isolated styling and don't benefit from Tailwind utilities. Other components benefit from design token propagation and utility-class consistency. This matches the existing pattern — the codebase already splits between these two approaches.

**Action:** Remove the raw CSS in `my-app.css` (the `nav { background: #eee }` block) and replace with Tailwind utilities in the template.

### Decision 4: Page Transition Animation Strategy

**Choice:** CSS-based view transitions using Aurelia 2 router lifecycle hooks.

**Rationale:** Aurelia 2's router supports `canLoad`/`loading`/`attached`/`detaching` lifecycle hooks. We can add CSS transition classes during `attached` (enter) and trigger exit animations via a shared transition service before `router.load()`. This avoids heavy animation libraries.

**Implementation:**
- Wrap `<au-viewport>` in a transition container
- Fade/slide animation: `opacity 0→1` + `translateY 20px→0` on enter
- ~300ms duration, ease-out timing
- No animation library needed (CSS transitions only)

### Decision 5: Font Strategy

**Choice:** Google Fonts with `Outfit` for display headings, `system-ui` for body text.

**Rationale:** `Outfit` is a geometric sans-serif with bold weights that work well for the mega-typography dashboard cards. It's free, performant (variable font), and has a modern music-app aesthetic. Using `system-ui` for body avoids additional font download for smaller text.

**Alternative considered:** Inter — excellent readability but less distinctive for headlines. Rejected for display use but suitable as body font alternative.

**Implementation:**
- Preload font in `index.html` via `<link rel="preconnect">` + `<link rel="stylesheet">`
- Define in `@theme` as `--font-display`
- Apply to hero copy, card artist names, section headings

### Decision 6: Region Setup Implementation

**Choice:** Bottom sheet overlay on first dashboard access with blurred background.

**Rationale:** This matches the UX specification's "Just-in-Time" approach — the region setup appears exactly when it's needed (before showing location-based events) rather than during onboarding. The blurred dashboard behind creates anticipation.

**Implementation:**
- New `region-setup-sheet` component (Aurelia 2 custom element)
- Triggered by `DashboardService` when user has no region set
- Prefecture dropdown (47 prefectures) with major city quick-select
- On selection: saves via `UserService.UpdateRegion` RPC, closes sheet, unblurs dashboard
- CSS: `backdrop-filter: blur(12px)` on overlay

### Decision 7: SVG Icon System

**Choice:** Inline SVG icons replacing Unicode emoji in Detail Sheet and Toast.

**Rationale:** Unicode emoji render differently across platforms (Android vs iOS vs Windows). SVG provides consistent, scalable, brand-aligned iconography. Using inline SVG avoids icon library dependencies.

**Implementation:**
- Create `src/components/icons/` directory with SVG components
- Icons needed: calendar, map-pin, link, ticket, share
- Apply `currentColor` for theme-aware coloring

## Risks / Trade-offs

**[Risk: Font loading delay]** → Mitigate with `font-display: swap` and preconnect. Body text uses system-ui as fallback so there's no FOUT for most content.

**[Risk: Dark theme contrast]** → Some artist-generated HSL colors may have poor contrast on dark backgrounds. Mitigate by adjusting `artistColor()` lightness range from `45%` to `55-65%` for dark backgrounds, and ensuring text on cards maintains WCAG AA ratio.

**[Risk: ShadowDOM token isolation]** → ShadowDOM components (DnaOrbCanvas, LoadingSequence) don't inherit Tailwind CSS custom properties. Mitigate by passing theme values via CSS custom properties on `:host` or using `shadowCSS()` with token references.

**[Risk: Performance regression from animations]** → Page transitions and scroll animations add rendering overhead. Mitigate by using CSS-only transitions (GPU-accelerated `transform`/`opacity`), `will-change` hints, and `prefers-reduced-motion` media query to disable for users who prefer it.

**[Risk: Scope creep]** → 50+ identified improvements could expand indefinitely. Mitigate by strict phasing — Phase 1 (design system + critical fixes) must ship before Phase 2 (polish) begins.
