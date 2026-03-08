## Context

The app shell (`my-app.html`) currently wraps `<main>` and `<bottom-nav-bar>` in a `min-h-screen` div. The bottom nav uses `position: fixed; bottom: 0` via Tailwind's `fixed inset-x-0 bottom-0` classes, and additionally uses the Popover API (`popover="manual"` + `showPopover()`) to promote itself to the browser's top layer. This causes the nav to render centered in the viewport (rather than at the bottom) because the UA stylesheet for popover elements applies `position: fixed; inset: 0; width: fit-content; height: fit-content; margin: auto`, overriding the intended `bottom: 0` positioning.

Each page (dashboard, etc.) compensates for the fixed nav by manually applying `h-screen pb-14`. The `user-home-selector` dialog can be dismissed by backdrop click or ESC during onboarding, even though home area selection is mandatory at Step 3. Additionally, several Tailwind physical directional classes and two `100vh` declarations remain despite the modern-css-platform spec.

## Goals / Non-Goals

**Goals:**
- Fix the bottom nav bar position by replacing `position: fixed` + popover with a CSS Grid app shell
- Prevent the home selector from being dismissed during onboarding
- Eliminate all physical directional Tailwind classes in favor of logical equivalents
- Replace remaining `100vh` with `100dvh`

**Non-Goals:**
- Refactoring `position: absolute` used for decorative overlays (gradient overlays, badges) — these are valid uses
- Refactoring the toast-notification or coach-mark popover usage — these are genuine popover/overlay use cases, not layout
- Adding RTL language support — logical properties are forward preparation only
- Changing the onboarding flow logic or step progression

## Decisions

### Decision 1: CSS Grid app shell with `grid-template-rows: 1fr min-content`

**Choice:** Replace the current `min-h-screen` wrapper + fixed nav with a CSS Grid container.

```
my-app.html layout:
┌─────────────────────────────────────┐
│ div.grid.grid-rows-[1fr_min-content]│
│     .h-dvh                          │
│ ┌─────────────────────────────────┐ │
│ │ <main class="overflow-y-auto">  │ │  ← 1fr (scrollable)
│ │   <au-viewport/>                │ │
│ │   <pwa-install-prompt/>         │ │
│ │   <notification-prompt/>        │ │
│ │ </main>                         │ │
│ ├─────────────────────────────────┤ │
│ │ <bottom-nav-bar/>               │ │  ← min-content (natural height)
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Rationale:** Grid keeps the nav in document flow. `1fr` naturally fills remaining space. `min-content` sizes the nav to its intrinsic height. No padding hacks, no popover, no z-index needed.

**Alternative considered:** `position: sticky; bottom: 0` — still requires the element to be at the end of a scroll container and can behave unexpectedly with nested scroll contexts. Grid is more predictable.

### Decision 2: Move prompts inside `<main>`

**Choice:** Move `<pwa-install-prompt>` and `<notification-prompt>` inside the `<main>` element so they scroll with content and live within the `1fr` row.

**Rationale:** These prompts are part of the page content flow, not persistent chrome. Placing them inside `<main>` keeps the grid structure clean (only 2 rows: content + nav).

### Decision 3: `required` bindable on `user-home-selector`

**Choice:** Add `@bindable required = false` to `UserHomeSelector`. When `true`, `handleBackdropClick` becomes a no-op (returns early). `handleCancel` always calls `preventDefault()` to suppress the browser's native ESC-to-close behavior on `<dialog>`; it only calls `close()` when `required` is `false`.

**Rationale:** The component is reused in both onboarding (mandatory) and settings (optional). A bindable cleanly separates the two contexts without forking the component. Dashboard passes `required.bind="isOnboarding"`.

**Alternative considered:** Creating a separate `OnboardingHomeSelector` wrapper — rejected as unnecessary duplication for a single behavioral flag.

### Decision 4: Physical-to-logical Tailwind class mapping

**Mapping applied in HTML templates:**

| Physical | Logical |
|----------|---------|
| `ml-*` | `ms-*` |
| `mr-*` | `me-*` |
| `pl-*` | `ps-*` |
| `pr-*` | `pe-*` |
| `left-*` | `start-*` |
| `right-*` | `end-*` |
| `text-left` | `text-start` |
| `text-right` | `text-end` |
| `rounded-l-*` | `rounded-s-*` |
| `rounded-r-*` | `rounded-e-*` |
| `border-l-*` | `border-s-*` |
| `border-r-*` | `border-e-*` |

**Rationale:** Tailwind v4 supports logical property utilities natively. This aligns HTML templates with the CSS-side logical property enforcement already in place via Stylelint.

### Decision 5: `100vh` to `100dvh`

**Choice:** Replace `100vh` with `100dvh` in `discover-page.css` and `loading-sequence.css`.

**Rationale:** `100dvh` adapts to mobile browser chrome (address bar show/hide), preventing content overflow on iOS Safari. The app shell itself uses `h-dvh` (Tailwind's `100dvh` utility).

## Risks / Trade-offs

**[Risk] Pages that set their own height constraints may break** → Each page that currently uses `h-screen pb-14` must have those classes removed. The grid shell's `overflow-y-auto` on `<main>` becomes the single scroll container.

**[Risk] `show.bind="showNav"` with Grid rows** → When `showNav` is `false`, Aurelia applies `display: none` on the nav. A grid child with `display: none` collapses its row, so `1fr` naturally fills the full height. No additional handling needed.

**[Risk] `overflow-y-auto` on `<main>` changes scroll context** → Previously, each page managed its own scroll. Now `<main>` is the scroll container. Pages with internal scroll areas (e.g., Live Highway horizontal scroll) should be unaffected since they use inline-direction scroll. Verify during testing.

**[Risk] `translate-x-*` classes (settings toggle)** → Physical `translate-x-*` has no logical Tailwind equivalent yet. These are left as-is since transforms are not directional in the same way as spacing.
