## Context

The Liverty Music frontend is an Aurelia 2 application using Vite, TailwindCSS v4, and `@aurelia/router`. Authentication uses Zitadel via `oidc-client-ts`. Currently there is no onboarding flow — after auth callback, users land on a basic welcome page. No animation or physics libraries are installed.

This design adds an Artist Discovery step to the post-authentication onboarding flow, using a "DNA Extraction" metaphor with interactive physics-based bubbles and a DNA Orb visual inventory.

## Goals / Non-Goals

**Goals:**
- Deliver a gamified artist discovery experience with physics-based bubble interactions
- Integrate backend ArtistService RPCs for initial artist seeding and similar artist chain reactions
- Show live event availability via toast notifications on artist follow
- Maintain 60fps performance on mobile devices
- Fit naturally into the existing Aurelia 2 routing and component architecture

**Non-Goals:**
- Backend API changes (use existing artist-following and live-events Connect-RPC services)
- Offline support or PWA features
- Custom WebGL shaders or 3D rendering (keep to 2D Canvas)
- Analytics or A/B testing infrastructure

## Decisions

### 1. Physics Engine: Matter.js

**Choice:** Matter.js for bubble physics simulation.

**Why over D3 force simulation:** Matter.js provides true rigid-body physics (collision detection, boundary constraints, natural bounce) which creates more satisfying bubble interactions. D3 force is designed for graph layouts, not game-like interactions.

**Why over custom physics:** Matter.js is well-maintained, lightweight (~80KB minified), and handles edge cases (stacking, overlap resolution) that would be time-consuming to implement.

### 2. Rendering: HTML5 Canvas with 2D Context

**Choice:** Single `<canvas>` element with 2D rendering context for all bubble and orb visuals.

**Why over DOM-based rendering:** With ~30+ animated elements, DOM manipulation and reflows become a performance bottleneck on mobile. Canvas provides direct pixel control and avoids layout thrashing.

**Why over WebGL:** 2D Canvas is sufficient for the visual complexity required (circles, gradients, particle effects). WebGL adds complexity without meaningful performance gain for this use case.

### 3. Component Architecture

```
src/routes/
  artist-discovery/
    artist-discovery-page.ts       # Route component, orchestrates state
    artist-discovery-page.html     # Template with canvas + overlay elements

src/components/
  dna-orb/
    dna-orb-canvas.ts              # Canvas renderer for orb + bubbles + animations
    bubble-physics.ts              # Matter.js world setup and bubble management
    orb-renderer.ts                # DNA Orb glass sphere rendering (gradients, particles)
    absorption-animator.ts         # Bubble-to-orb absorption animation controller

  toast-notification/
    toast-notification.ts          # Reusable toast component
    toast-notification.html        # Toast template

src/services/
  grpc-transport.ts               # Connect-RPC transport configured with VITE_API_BASE_URL
  artist-discovery-service.ts     # Orchestrates discovery state via ArtistService RPCs
```

**Why this structure:** Separates rendering concerns (canvas, physics, animation) from business logic (API calls, state). The canvas components are pure renderers; the service layer manages data flow and backend integration.

### 4. State Management: Service-Based with Aurelia DI

**Choice:** `ArtistDiscoveryService` as a singleton service managing discovery state (followed artists, available bubbles, orb state).

**Why over external state library:** The state is local to the discovery page and doesn't need global persistence. Aurelia's DI container provides clean singleton lifecycle management. Adding Redux/MobX for a single page is over-engineering.

### 5. Last.fm API Integration: Backend RPC via Connect-RPC

**Choice:** Call the backend `ArtistService` RPCs (`ListTop`, `ListSimilar`) via Connect-RPC instead of calling the Last.fm API directly from the frontend.

**Why:** The Last.fm API key is a secret credential. Embedding it in client-side JavaScript via `VITE_LASTFM_API_KEY` exposes the key in the browser bundle, allowing anyone to extract and abuse it. The backend already provides `ArtistService.ListTop` and `ArtistService.ListSimilar` RPCs that proxy Last.fm with proper rate limiting and error handling. The TypeScript RPC client is available via BSR (`@buf/liverty-music_schema.connectrpc_es`).

### 6. Onboarding Flow Integration

**Choice:** Add `/artist-discovery` route, redirect from auth callback when user is new (first login).

**Why:** The existing router supports standard route additions. A route-based approach keeps the discovery page independent and testable. The auth service can track whether a user has completed onboarding via a backend flag.

## Risks / Trade-offs

- **[Mobile Performance]** → Canvas with requestAnimationFrame + object pooling for particles. Profile on low-end devices early. Reduce bubble count if needed (20 instead of 30).
- **[Backend RPC Latency]** → Backend handles Last.fm rate limiting internally. Frontend caches RPC responses in-memory during session. Fall back to empty state if backend is unavailable.
- **[Matter.js Bundle Size (~80KB)]** → Lazy-load via dynamic import on the artist-discovery route. Does not affect initial load.
- **[Canvas Accessibility]** → Canvas content is not accessible to screen readers. Add ARIA live region with text description of current state and keyboard controls for bubble selection.
- **[Aurelia 2 + Canvas Integration]** → Canvas lifecycle managed via `attached()`/`detaching()` hooks. Physics loop starts/stops with component lifecycle to prevent memory leaks.
