## Why

The discover page onboarding experience has two UX problems: (1) the persistent HUD guidance occupies a grid row, reducing the bubble area and creating layout issues (search bar oversized due to missing icon sizing, bubble container clipped at top), and (2) the numeric countdown ("あと2組！") creates a "forced task" feel instead of making artist discovery intrinsically fun. Replacing the HUD with a one-time Popover API guide and adding accumulating orb visual effects will make following artists feel rewarding on every tap while maximizing screen real estate for the bubble UI.

## What Changes

- **Remove** the persistent onboarding HUD (`onboarding-hud`, progress dots, staged guidance messages) from the discover page grid layout
- **Add** a Popover API-based onboarding guide that appears once on discover page entry and dismisses via light-dismiss
- **Add** accumulating orb visual effects: each follow injects the bubble's color into the orb with an easing-based intensity curve, making the orb progressively more vibrant and chaotic
- **Simplify** the discover page grid from 4 rows (`auto auto auto 1fr`) to 3 rows (`auto auto 1fr`), maximizing bubble area
- **Fix** search bar icon sizing (missing explicit dimensions on `.search-icon` and `.clear-button` causing layout overflow)
- **Use** modern CSS features for popover animations (`@starting-style`, `:popover-open`, `transition-behavior: allow-discrete`) instead of JS-driven class toggling

## Capabilities

### New Capabilities
- `onboarding-popover-guide`: One-time dismissible popover guide shown on discover page entry during onboarding, using native Popover API with CSS-only entry/exit animations

### Modified Capabilities
- `onboarding-guidance`: Remove persistent HUD, staged progress messages, and progress bar; replace with popover guide and visual orb feedback
- `artist-discovery-dna-orb-ui`: Enhance orb with accumulating `baseIntensity` (easing curve, +per-follow), increased color injection (10-15 particles per follow using bubble's existing hue), and persistent swirl intensity that ratchets up with each follow
- `discover`: Fix search bar layout (icon sizing), simplify grid to 3 rows

## Impact

- **Frontend only** — no backend or proto changes
- `src/routes/discover/discover-page.html` — remove HUD markup, add popover element, simplify grid
- `src/routes/discover/discover-page.css` — remove HUD styles, add popover styles with modern CSS, fix search icon sizing, update grid-template-rows
- `src/routes/discover/discover-page.ts` — remove guidance message logic, add popover show/hide on attach, simplify onboarding state
- `src/components/dna-orb/orb-renderer.ts` — add `baseIntensity` property with easing accumulation, increase `injectColor` particle count
- `src/components/dna-orb/dna-orb-canvas.ts` — wire `baseIntensity` updates on follow events
- E2E tests (`e2e/onboarding-flow.spec.ts`) and unit tests will need updates to reflect removed HUD and new popover
- Existing spotlight/coach-mark system for dashboard transition is **unchanged**
