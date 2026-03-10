## Context

The frontend has 300+ Vitest unit tests covering ViewModel logic and services, plus 4 Playwright E2E tests for PWA behavior. None test CSS layout. Layout bugs like the 7-layer `height: 100%` relay chain failure are invisible to CI.

The app has 8 routes with three distinct layout patterns:
- **Full-bleed** (discover, loading-sequence): flex-col, overflow:hidden, fill viewport
- **Scrollable content** (dashboard, my-artists, tickets): flex-col, fixed header + scrollable body
- **Root scroll** (settings): single container with overflow-y:auto

Four routes require OIDC auth (dashboard, my-artists, tickets, settings). The remaining routes (discover, loading-sequence, welcome, not-found) are publicly accessible.

## Goals / Non-Goals

**Goals:**
- Detect layout regressions (element sizing, overflow, containment) automatically in CI.
- Cover the shell layout (Grid auto-stretch, bottom-nav positioning), public routes, and authenticated routes (settings) via `storageState`.
- Keep test execution under 3 seconds for the full layout suite.
- Use Playwright `boundingBox()` and `toHaveCSS()` assertions — no screenshot diffing.

**Non-Goals:**
- Visual regression testing (pixel-diff / `toHaveScreenshot()`). That's a separate future effort.
- Testing all authenticated routes. Settings page is covered via `storageState`; remaining auth routes (dashboard, my-artists, tickets) use RPC mocks and share the same scrollable layout pattern.
- Testing Canvas rendering content (Matter.js bubble positions). Only Canvas element sizing.
- Testing animations or transitions.

## Decisions

### 1. Playwright Layout Assertions over VRT

**Choice:** `boundingBox()` + `toHaveCSS()` assertions.
**Alternative:** `toHaveScreenshot()` pixel-diff.
**Rationale:** Layout assertions are 5-10x faster (~300ms vs ~2s per test), produce no baseline images to manage, and are deterministic across OS/font rendering. They test the structural contract ("canvas fills parent") not visual appearance.

### 2. Mobile-first viewport (390×844)

**Choice:** Test at iPhone 14 dimensions as the single viewport.
**Alternative:** Multi-viewport matrix (mobile + tablet + desktop).
**Rationale:** The app is a mobile-first PWA. The primary risk is mobile layout breakage. A single viewport keeps the suite fast. Desktop viewport tests can be added later.

### 3. RPC route mocking via `page.route()`

**Choice:** Intercept Connect-RPC calls with `page.route()` returning static JSON.
**Alternative:** Run a mock backend server.
**Rationale:** `page.route()` is zero-infrastructure, runs in-process, and makes tests independent of backend availability. Layout tests only need enough data to render the page structure, not realistic payloads.

### 4. Dedicated `e2e/layout/` directory

**Choice:** Separate layout tests from functional E2E tests in `e2e/layout/`.
**Alternative:** Mix layout assertions into existing E2E test files.
**Rationale:** Layout tests have a distinct purpose (structural invariants) and different running requirements (mock RPC, specific viewport). Separation makes it clear what each test file is responsible for.

### 5. Scope: shell, public routes, and settings (authenticated)

**Choice:** Test shell layout, discover page, dashboard (via RPC mocks), and settings (via `storageState`). Loading-sequence excluded — it is a transient page that navigates away immediately after `loading()` resolves.
**Alternative:** Include all routes or only public routes.
**Rationale:** Public routes cover the highest-risk layouts (Grid shell, Canvas sizing, full-bleed). Settings validates the `storageState` approach for authenticated routes. Dashboard uses RPC mocks without auth. Loading-sequence is untestable without coupling to Aurelia router internals.

## Risks / Trade-offs

**[Flaky boundingBox on slow CI]** → Set explicit `waitForSelector` before measuring. Layout assertions don't depend on animation timing, so flakiness risk is low.

**[Canvas element may report 0×0 before initialization]** → Wait for the Canvas `width`/`height` attributes to be set (dna-orb-canvas sets these on `attaching()`).

**[RPC mock maintenance]** → Mock responses are minimal (just enough for page render). Structure is unlikely to change frequently. If it does, a shared mock fixture file keeps updates centralized.

**[Auth route coverage]** → Settings page is tested via `storageState` in the `authenticated-mobile` project. Dashboard is tested via RPC mocks without auth. The remaining scrollable routes (my-artists, tickets) share the same layout pattern as dashboard.
