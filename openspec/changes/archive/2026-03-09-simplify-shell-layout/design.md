## Context

The app shell (`my-app`) currently uses CSS Grid (`grid-template-rows: 1fr min-content`) with a `<main>` wrapper containing `au-viewport`, prompts, and overlays. Route components must explicitly declare `height: 100%` at every nesting level to receive a definite height from the shell — a 7-layer relay chain that breaks silently when any link is missing.

Recent bugs caused by this architecture:
- Discover page bubbles invisible (canvas at 0×0) due to Tailwind `.container` class collision breaking the height chain
- Overlay components (`pwa-install-prompt`, `notification-prompt`) creating implicit grid rows in `<main>`
- Shell-level `overflow-y: auto` on `au-viewport` conflicting with routes that need their own scroll control

The frontend uses Aurelia 2 with TailwindCSS v4, Vite, and the View Transitions API for route animations.

## Goals / Non-Goals

**Goals:**
- Eliminate the height relay chain so route components receive a definite size automatically
- Make each route self-contained for scroll behavior
- Prevent class name collisions with Tailwind utility classes
- Keep overlay rendering in the browser top layer, independent of DOM position

**Non-Goals:**
- Changing visual design or user-facing behavior
- Modifying the `dna-orb-canvas` Shadow DOM component
- Changing the View Transitions API integration
- Refactoring route component internal logic

## Decisions

### 1. Remove `<main>` wrapper, make `au-viewport` a direct grid child

**Decision**: Remove the `<main>` element. `au-viewport` becomes a direct child of the `my-app` grid.

**Rationale**: The `<main>` wrapper existed to group prompts and viewport, but prompts now use the browser top layer (Popover API / `<dialog>`). The extra nesting adds complexity without benefit. `au-viewport` as a direct grid child in the `1fr` row receives a definite height from the grid automatically.

**Alternative considered**: Keep `<main>` but simplify its styles. Rejected because the wrapper provides no layout value once overlays are in the top layer.

### 2. Make `au-viewport` a CSS Grid container (stretch behavior)

**Decision**: Set `au-viewport { display: grid; }` so its children (route components) auto-stretch to fill both axes.

**Rationale**: CSS Grid children stretch by default (`align-items: stretch`, `justify-items: stretch`). This means route custom elements automatically get the full width and height of `au-viewport` without any explicit `height: 100%` declaration. The entire relay chain is eliminated in one rule.

**Alternative considered**: Use `display: flex; flex-direction: column` with `flex: 1` on children. Rejected because Grid stretch is more robust — it works in both axes simultaneously and doesn't require children to declare flex properties.

### 3. Rename `.container` to `.discover-layout` in discover-page

**Decision**: Rename the custom `.container` class to `.discover-layout` to avoid collision with Tailwind v4's `.container` utility.

**Rationale**: Tailwind v4 generates a `.container` class that applies `width: 100%` and `align-items: center` (among other rules). When discover-page uses `.container` in light DOM, both Tailwind's and the component's rules apply, causing unexpected layout behavior (flex children shrinking to width 0).

**Alternative considered**: Use Tailwind's `@layer` or `!important` to override. Rejected because renaming is simpler, clearer, and eliminates the conflict entirely.

### 4. Route-owned scrolling

**Decision**: Remove any shell-level `overflow-y: auto` from `au-viewport`. Each route component that needs scrolling applies `overflow-y: auto` on its own scrollable container.

**Rationale**: Different routes have different scroll needs:
- **Discover page**: No scroll on the outer container (canvas fills viewport), but search results scroll independently
- **Settings page**: Entire page scrolls vertically
- **Dashboard**: Scrolls vertically with sticky headers possible

A single shell-level scroll container cannot accommodate these varied needs. Route-level control is more flexible and explicit.

### 5. Overlay placement

**Decision**: Keep overlay components (`pwa-install-prompt`, `notification-prompt`, `error-banner`) as children of `my-app` (outside `au-viewport`), relying on the Popover API and `<dialog>` for top-layer rendering.

**Rationale**: These elements use `popover="manual"` or `<dialog>.showModal()`, which renders them in the browser's top layer regardless of DOM position. Placing them outside `au-viewport` ensures they never interfere with the grid layout. They don't need a `<main>` wrapper to be grouped — they can be direct children of `my-app` since they render in the top layer.

## Risks / Trade-offs

**[Risk]** Route components that currently rely on `height: 100%` may behave differently when stretched by Grid.
→ **Mitigation**: Grid stretch and `height: 100%` produce the same result when the parent has a definite height. Verify each route visually after the change.

**[Risk]** Aurelia 2's `au-viewport` may inject wrapper elements that break the Grid parent-child relationship.
→ **Mitigation**: Aurelia 2's viewport renders the route component directly as a child of `au-viewport`. Verified in current codebase — no intermediate wrappers.

**[Risk]** Removing `<main>` loses semantic landmark for accessibility.
→ **Mitigation**: Add `role="main"` to `au-viewport`, or wrap only the viewport in a semantic `<main>` that has `display: contents` (passes through grid without creating a box). The latter is preferred for HTML validation.

**[Trade-off]** Moving scroll control to routes means every scrollable route must remember to add `overflow-y: auto`.
→ **Accepted**: This is more explicit and less error-prone than a shell-level scroll that silently applies to all routes regardless of need.
