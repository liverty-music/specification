## 1. Project Setup & Dependencies

- [x] 1.1 Install Matter.js (`matter-js`) and its TypeScript types (`@types/matter-js`)
- [x] 1.2 Create the artist-discovery route directory structure (`src/routes/artist-discovery/`)
- [x] 1.3 Register the `/artist-discovery` route in `my-app.ts` with lazy loading

## 2. Last.fm API Service

- [x] 2.1 Create `src/services/lastfm-service.ts` with `getTopArtists(country)` method calling `geo.getTopArtists`
- [x] 2.2 Add `getSimilarArtists(artistName)` method calling `artist.getSimilar` with 300ms debounce
- [x] 2.3 Add in-memory response caching for similar artist results within the session

## 3. Artist Discovery Service

- [x] 3.1 Create `src/services/artist-discovery-service.ts` managing discovery state (available bubbles, followed artists, orb intensity)
- [x] 3.2 Implement `followArtist(artist)` method that calls the backend artist-following Connect-RPC service
- [x] 3.3 Implement `checkLiveEvents(artistName)` method that queries the backend live-events service and returns event availability

## 4. Physics Engine & Bubble Management

- [x] 4.1 Create `src/components/dna-orb/bubble-physics.ts` with Matter.js world setup (gravity, boundaries, collision detection)
- [x] 4.2 Implement bubble creation with initial random positions and physics bodies for ~30 artist bubbles
- [x] 4.3 Implement bubble removal from physics world on artist selection (tap/click handler)
- [x] 4.4 Implement similar artist bubble spawning — new bubbles emerge from the selected bubble's position with "pop" animation

## 5. Canvas Rendering

- [x] 5.1 Create `src/components/dna-orb/dna-orb-canvas.ts` with Aurelia 2 component lifecycle (`attached`/`detaching`) managing the canvas element and requestAnimationFrame loop
- [x] 5.2 Implement bubble rendering — circles with artist name labels, artist images as circular textures
- [x] 5.3 Create `src/components/dna-orb/orb-renderer.ts` — render the DNA Orb at the bottom of the canvas with glass sphere gradient, inner glow, and swirling particle effects
- [x] 5.4 Implement orb visual evolution — increase glow intensity, color saturation, and particle density proportional to followed artist count

## 6. Absorption Animation

- [x] 6.1 Create `src/components/dna-orb/absorption-animator.ts` with animation controller for bubble-to-orb transitions
- [x] 6.2 Implement shrink + path-trace animation (bubble shrinks while following a curved Bezier path toward the orb)
- [x] 6.3 Implement dissolve effect on absorption (fade + particle burst at orb surface)

## 7. Toast Notifications

- [x] 7.1 Create `src/components/toast-notification/toast-notification.ts` and `.html` — reusable toast component with slide-in from top, 2-3 second display, and fade-out
- [x] 7.2 Integrate toast trigger in artist discovery flow — show "🎫 [Artist Name] has upcoming live events!" when `checkLiveEvents` returns true

## 8. Completion & Navigation

- [x] 8.1 Implement the "View Live Schedule (X artists)" button rendered on/near the DNA Orb, visible when follow count >= 1
- [x] 8.2 Wire button tap to navigate to the loading sequence / dashboard route

## 9. Onboarding Flow Integration

- [x] 9.1 Update auth callback flow to redirect new users (first login) to `/artist-discovery` instead of the welcome page
- [x] 9.2 Ensure returning users bypass artist discovery and go directly to dashboard

## 10. Accessibility & Performance

- [x] 10.1 Add ARIA live region describing current discovery state (number of artists available, number followed) and keyboard controls for bubble selection
- [x] 10.2 Profile canvas rendering on mobile devices and optimize (reduce bubble count, object pooling for particles) if frame rate drops below 60fps

## 11. Migrate Last.fm Direct Calls to Backend RPC

- [x] 11.1 Install Connect-RPC packages (`@connectrpc/connect`, `@connectrpc/connect-web`) and BSR-generated TypeScript client (`@buf/liverty-music_schema.connectrpc_es`)
- [x] 11.2 Create `src/services/grpc-transport.ts` — configure Connect-RPC transport using `VITE_API_BASE_URL`
- [x] 11.3 Rewrite `artist-discovery-service.ts` — replace `ILastfmService` dependency with `ArtistService` RPC client (`ListTop` for initial artists, `ListSimilar` for chain reactions)
- [x] 11.4 Delete `src/services/lastfm-service.ts` and remove all references to `ILastfmService`
- [x] 11.5 Remove `VITE_LASTFM_API_KEY` from environment files and `vite-env.d.ts`
- [x] 11.6 Update `vite-env.d.ts` to declare `VITE_API_BASE_URL`
