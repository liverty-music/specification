## Why

Current UI implementation is functionally correct but visually at "prototype level" — it lacks brand identity, visual polish, animation, and the immersive experience described in the UX specification. The gap between the envisioned "exciting, gamified onboarding" and the actual UI (plain white backgrounds, raw Tailwind defaults, scaffold page titles, inconsistent theming) undermines user engagement and first impressions. A comprehensive design refinement is needed to bring the frontend up to production quality before user-facing launch.

## What Changes

- Establish a unified **design system** (color palette, typography scale, spacing, shadows) as Tailwind v4 theme tokens
- Unify the **app shell** — remove scaffold nav during onboarding, fix page title/favicon, redesign auth UI, add page transition animations
- Redesign the **landing page** — dark theme, brand logo, hero animation, proper Google/Passkey CTA styling
- Enhance **Artist Discovery** visuals — per-artist bubble colors, onboarding guidance overlay, orb label, background starfield
- Upgrade **Loading Sequence** — progress indicator, step animation, visual effects beyond text-only
- Polish **Dashboard** — larger mega-typography, card gradient/shadow, scroll animations, date separator styling
- Improve **Detail Sheet** — spring animation, swipe-to-dismiss, SVG icons replacing emoji
- Enhance **Toast Notifications** — vibrant design with accent colors, bounce-in animation
- Add **Region Setup** bottom sheet — just-in-time area input on first dashboard access (per spec)

## Capabilities

### New Capabilities
- `design-system`: Unified design tokens (colors, typography, spacing, shadows) as Tailwind v4 theme configuration, ensuring visual consistency across all screens
- `app-shell-layout`: Application shell structure including conditional navigation, page transitions, brand elements (logo, favicon, page title), and responsive layout wrapper

### Modified Capabilities
- `landing-page`: Visual design upgrade — dark theme background, branded CTA button styling, hero entrance animation, service logo display
- `artist-discovery-dna-orb-ui`: Bubble visual differentiation (per-artist colors), onboarding guidance overlay, orb label text, background particle effects
- `loading-sequence`: Visual richness — progress bar/step indicators, animated visual effects beyond text-only fade
- `typography-focused-dashboard`: Card design polish (gradients, shadows, animation), enlarged mega-typography, improved date separators, scroll reveal animations
- `frontend-onboarding-flow`: Region setup bottom sheet UI on first dashboard access, page-to-page transition animations

## Impact

- **Frontend codebase** (`src/`): All template files, CSS, and component TypeScript files will be modified
- **Tailwind config**: New theme extension with design tokens (may require `tailwind.config.ts` or CSS `@theme` block)
- **Static assets**: New logo/favicon/font files to be added
- **index.html**: Updated title, favicon links, font preload
- **my-app.css**: Complete rewrite to remove scaffold styles
- **No backend changes**: This is purely a frontend visual refinement
- **No API changes**: No protobuf or RPC changes required
