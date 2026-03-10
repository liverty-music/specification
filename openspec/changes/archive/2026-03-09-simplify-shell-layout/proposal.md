## Why

The current app shell layout relies on a 7-layer `height: 100%` relay chain (`my-app` → `main` → `au-viewport` → route component → inner containers → canvas host → canvas). Any break in this chain — such as a missing `height`, a class name collision, or a framework-injected wrapper — collapses the layout silently (e.g., canvas renders at 0×0, bubbles disappear). This fragility has caused recurring bugs that are hard to diagnose. A simpler layout using modern CSS Grid auto-stretch behavior would eliminate the relay chain entirely and make each route self-contained.

## What Changes

- **Remove the `<main>` wrapper element**: `au-viewport` becomes a direct grid child of the app shell, removing one unnecessary nesting layer.
- **Make `au-viewport` a CSS Grid container**: Route components placed inside a Grid container auto-stretch to fill both axes without needing explicit `height: 100%`. This eliminates the height relay chain.
- **Rename `.container` class in discover-page**: Rename to a non-colliding name (e.g., `.discover-layout`) to avoid conflicts with Tailwind v4's `.container` utility class.
- **Move overlay components to top-layer only**: PWA install prompt, notification prompt, and error banner use Popover API / `<dialog>` and render in the browser's top layer. They no longer need to be positioned within `<main>` to avoid grid row interference — they can be placed anywhere in the DOM.
- **Route-owned scrolling**: Each route component manages its own `overflow-y: auto` where needed, rather than relying on a shell-level scrolling container. This gives routes full control over their scroll behavior.

## Capabilities

### New Capabilities

_(none — this is a structural refactoring of existing layout behavior)_

### Modified Capabilities

- `app-shell-layout`: The height propagation strategy changes from explicit `height: 100%` relay to CSS Grid auto-stretch. The `<main>` wrapper is removed. `au-viewport` becomes both a direct grid child and a Grid container. Scroll responsibility moves from shell to individual routes.

## Impact

- **Frontend only** — no backend, API, or protobuf changes.
- **`my-app.html` / `my-app.css`**: Shell template and styles restructured.
- **All route components**: Remove explicit `height: 100%` declarations that were part of the relay chain. Routes that need scrolling add their own `overflow-y: auto`.
- **`discover-page.css`**: Rename `.container` to avoid Tailwind collision.
- **`dna-orb-canvas`**: No changes needed — Shadow DOM `:host { display: block; width: 100%; height: 100% }` works correctly once the parent provides a definite size via Grid.
- **Overlay components** (`pwa-install-prompt`, `notification-prompt`, `error-banner`): DOM placement may change but rendering behavior is unchanged (top-layer).
- **No breaking changes to user-facing behavior** — visual output and interactions remain identical.
