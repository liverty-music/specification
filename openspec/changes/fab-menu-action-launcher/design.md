## Context

See `proposal.md` — Why. This is a fan-web (Aurelia 2) presentation-layer change;
no backend/proto involved. Relevant current state:

- The three controls live in the dashboard `page-header` trailing slot:
  `artist-filter-bar` (its own trigger + bottom sheet), a `.beam-toggle` button
  (session/localStorage state on the route), and `page-help` (its own `?` trigger
  + per-page bottom sheet). A `mode-swap` button (My Timetable ↔ All Nearby) sits
  there too. Beam and filter render only in My Timetable mode; help renders on
  discovery/dashboard/my-artists.
- The app avoids z-index stacking by rendering overlays in the browser **top
  layer** via `popover`/`dialog` (`snack-bar`, `bottom-sheet`, `coach-mark`).
  `snack-bar` is the precedent for a global overlay in `app-shell` driven by an
  injectable service.
- The shell is a 2-row grid: viewport + `bottom-nav-bar` (row 2, `position:
  relative`, `env(safe-area-inset-bottom)` padding). A fixed FAB at the viewport's
  bottom-right would overlap the nav.
- Design tokens are oklch, dark-only, CUBE CSS with `@layer`/`@scope`. Motion
  tokens are duration-based (`--transition-*`); there is no spring layer. Matter.js
  physics exists only inside the dna-orb canvas.

## Goals / Non-Goals

**Goals:**
- One global launcher owning all four dashboard actions; header becomes
  title-only.
- Per-route contextual action sets with **no stale registrations** across
  navigation or mode changes.
- M3 Expressive feel (shape morph + spring) using portable modern CSS, mapped onto
  the existing oklch token system, at the **canonical M3 values** (springs, shape
  scale, state layers, touch targets) rather than ad-hoc numbers.
- Correct disclosure accessibility, focus handling, and reduced-motion behavior.
- Fidelity to the official M3 FAB Menu guidance — see **M3 References** below;
  implementation MUST consult it, not reproduce it from memory.

**Non-Goals:**
- No light theme. Single dark ("stage-lit") theme stays; roles are defined so a
  light theme *could* be generated later without touching components.
- No new physics engine. Springs are CSS `cubic-bezier`/`linear()` approximations,
  not a runtime solver.
- The filter and help **sheets are not rewritten** — only their triggers move. The
  filter sheet keeps its dashboard-owned bindings.
- No anchor-positioning dependency (see Decisions).

## Decisions

### D1 — Global launcher driven by a singleton service (the snack-bar model)
`<fab-menu>` mounts once in `app-shell` and binds to `IFabMenuService.actions`
(an `@observable` array; Aurelia intercepts `push`/`splice`). Routes contribute
actions through the service rather than the shell reaching into routes.
- **Why**: The FAB is global (one position/morph/spring implementation) but its
  contents are page-local. A DI singleton decouples rendering from ownership,
  exactly as `snack-bar` does. Alternatives: (a) route-`data`-declared actions —
  rejected because it can't express live state (beam on/off) or intra-route mode
  changes; (b) slot/portal projection from route up into the shell — rejected as
  fighting Aurelia's parent→child slot direction and more complex than a service.

### D2 — Registration returns a disposer; registration is owner-keyed
`register(owner, actions[])` returns a disposer. Routes call it in `attached()`,
push the disposer onto their `subscriptions`, and `dispose()` in `detaching()` —
the same lifecycle discipline the codebase already enforces for listeners. A
re-`register` by the same owner **replaces** that owner's set (idempotent), so a
mode change (`@watch('isAllNearby')` re-registering) never accumulates.
- **Why**: Stale FAB items after navigation is the predictable failure mode of a
  global registry; making the registration lifetime a disposable that mirrors
  subscriptions makes leaks structurally hard. Alternative: register/unregister by
  string id — rejected as more error-prone than a returned disposer.

### D3 — FAB is a launcher; sheets stay where they are; beam is inline
Each `FabAction` is `{ id, labelKey, icon, kind: 'command' | 'toggle', isOn?,
invoke }`. `command` actions call the existing surface (`pageHelp.open()`,
`filterBar.openSheet()`, `toggleMode()`); the `toggle` action (beam) flips state
inline in the panel and reflects `isOn()` via `aria-pressed`.
- **Why**: Preserves the complex, dashboard-owned filter sheet bindings and the
  per-page help content untouched, limiting the "two overlays stacked" moment to a
  single tap→sheet. Alternative: reimplement filter/help inside the FAB panel —
  rejected as high-risk churn for no user benefit.
- **Order & labels** (per requirement §4, bottom = closest to thumb, expanding
  upward). Dashboard My Timetable, bottom→top:
  1. beam — `レーザー演出切り替え` (toggle)
  2. filter — `コンサート一覧の絞り込み` (command)
  3. mode-swap — the other view's name (command)
  4. help — `ヘルプ` (command, top / least in-context)
  Every item is icon **+** text label; icon-only is disallowed. Exact label
  strings and per-page sets are pinned in the specs artifact.

### D4 — Top-layer Popover + CSS shape-morph + spring (no JS animation)
Panel is `popover="auto"` (top layer, native light-dismiss + Esc). Entry/exit use
`@starting-style` + `transition-behavior: allow-discrete` + `overlay` in the
transition list. Morph = animate `border-radius` + `scale` with
`transform-origin` at the FAB corner (M3 says border-radius morph covers this;
`clip-path` not needed). `+`→`×` is a `rotate`. New spring tokens
(spatial/effects families) added to `tokens.css`; **spatial** springs (bouncy) for
transform/scale/radius, **effects** (non-bouncy) for opacity/color.
- **Why**: Matches the app's established top-layer convention and needs no
  animation library. `linear()` and `cubic-bezier` springs are Baseline; `overlay`
  degrades to an instant swap on Firefox/Safari (acceptable). Alternative:
  View Transitions for the morph — deferred; heavier and unnecessary for a
  round↔rounded-rect change.
- **Canonical M3 motion tokens** (added to `tokens.css`; do not invent values —
  these are the M3 spring approximations and are easy to get subtly wrong):
  - `--md-spring-spatial: cubic-bezier(0.38,1.21,0.22,1.00)` @ **500ms** — panel
    open/expand, scale, morph.
  - `--md-spring-spatial-fast: cubic-bezier(0.42,1.67,0.21,0.90)` @ **350ms** —
    `+`↔`×` glyph rotate, small snappy moves.
  - `--md-spring-effects: cubic-bezier(0.34,0.80,0.34,1.00)` @ **200ms** — opacity
    and color (non-bouncy; a bouncing opacity looks broken).
  - **Assignment rule**: spatial (bouncy) for anything that moves/resizes
    (transform, scale, `border-radius`); effects (no overshoot) for opacity/color.
    Mixing them is the most common spring mistake.
- **Item entrance stagger** (requirement §5.1 "delightful transitions"): items rise
  in sequence, not all at once — per-item delay via `sibling-index()` (fallback
  `:nth-child` steps), ~30–50ms apart, on the effects curve. Closing reverses with
  a shorter stagger.
- **Shape scale** (morph endpoints, from the M3 shape scale): FAB closed =
  `--radius-full` (56px circle); expanded panel = `--radius-card` (≈`corner-large`,
  1rem). Animate `border-radius` between these two on the spatial curve.
- **Backdrop / contrast** (requirement §3.1 "strong contrast"): the panel takes
  `--md-color-menu-surface` (a raised surface tier) over an animated `::backdrop`
  scrim (`--md-color-scrim` at low alpha), transitioned with `display`/`overlay`
  `allow-discrete` per the top-layer recipe; the scrim also communicates the
  light-dismiss region. Reduced-motion keeps the scrim, drops its fade.
- **Close/non-spring motion**: the dismiss and backdrop fade use the standard
  effects curve/duration above, not a spatial spring (only entry/expand overshoots).

### D5 — Disclosure semantics, not an ARIA menu
The FAB is a `<button aria-expanded aria-controls="…">`; the panel is a
`role="group"` of plain `<button>`s. Focus moves to the first item on open and
returns to the FAB on close.
- **Why**: `role="menu"`/`menuitem` is a promise of full arrow-key roving
  navigation we are not implementing; the disclosure pattern is the correct,
  simpler contract (per web-design-specialist and modern-web-guidance). Reversing
  this later would be a breaking a11y change, so decide it now.

### D9 — Interaction fidelity: touch targets, state layers, emphasis budget
- **Touch targets** (requirement §3.2 "dynamic item size"): the FAB is 56px; every
  panel item has a **≥48px** active area (min-block-size), independent of label
  length. The animated visual shape never shrinks the hit box (animate visual
  `border-radius`/`transform`, not the clickable box).
- **State layers** (M3 state-layer opacities, on the `on-*` color of each element):
  hover ≈ 8%, focus ≈ 10%, pressed ≈ 10% overlays on the FAB and each item;
  the beam toggle's `aria-pressed` selected state gets a persistent selected layer.
  Rendered as an overlay so it composes with any fill; `:focus-visible` for the
  keyboard ring.
- **Emphasis budget** (M3 expressive-principles): intensity level = **"excellent"**
  — the FAB launcher is the screen's single hero moment (bold container color,
  larger shape, spring). Everything around it (header, items, sheets) stays
  **foundational**; do not add competing bounce/morph elsewhere on the page.
- **Why**: These are the M3 values most easily lost when building DIY on the web
  (M3 has no official web FAB Menu); pinning them here keeps contrast, reach, and
  restraint from silently degrading during implementation.

### D6 — Left-handed placement via logical properties + data attribute
`fab-menu[data-handed="left|right"]` swaps `inset-inline-*` and the panel
`transform-origin`; the value is persisted via an `adapter/storage/` entry and a
settings toggle, mirroring the beam preference.
- **Why**: Portable and framework-agnostic; avoids depending on CSS anchor
  positioning (still Chromium-led), which the single self-contained overlay does
  not otherwise need.

### D7 — Bottom-nav offset via a published CSS variable
`bottom-nav-bar` exposes its rendered height as `--bottom-nav-height` on its
`:scope`; the FAB computes `inset-block-end = calc(var(--bottom-nav-height) +
env(safe-area-inset-bottom) + var(--space-s))` when the nav is shown, and drops
the nav term when it is not.
- **Why**: Declarative, no `ResizeObserver`. FAB visibility follows the shell's
  existing `showNav` gate and `actions.length > 0`.

### D8 — "Dynamic Color" reinterpreted as a role-based token layer
Add `--md-color-*` role tokens (primary-container / on-primary-container /
menu-surface with strong contrast) mapped onto existing brand oklch values; reuse
the brand-tinted shadow (`--shadow-card-glow`) for FAB elevation (M3 level 3).
- **Why**: OS wallpaper-driven dynamic color is not a web concept; M3 treats a
  single dark theme as legitimate. Encoding roles (not raw colors) keeps contrast
  guarantees and leaves a future light theme to the token layer only.

## Risks / Trade-offs

- **[mode-swap folded into the FAB adds a tap to a high-frequency view switch]** →
  Chosen per product direction; mitigate by ordering it near the top and
  validating operation feel on a real device. If it reads as heavy, the header can
  reclaim mode-swap without affecting the launcher architecture.
- **[Global FAB whose contents/visibility change per page can feel inconsistent]**
  → Hide entirely at zero actions rather than showing an empty launcher; keep
  ordering stable across pages so muscle memory holds.
- **[`overlay`/`@starting-style` not universal]** → Feature degrades to an instant
  show/hide; core function (open/close/dismiss) is native Popover and unaffected.
- **[Stacked overlays: FAB panel → filter/help sheet]** → Limit the FAB to a
  launcher (D3); the panel closes as the sheet opens so only one overlay is active.
- **[Stale registrations on navigation]** → Disposer + owner-keyed replace (D2);
  covered by component tests asserting the action set after navigate and after a
  mode toggle.
- **[Reduced motion / vestibular]** → Every spring/morph has a
  `prefers-reduced-motion: reduce` path that lands the end state near-instantly so
  `transitionend`-dependent logic still fires.

## Migration Plan

Ship in slices, each independently verifiable in the browser:
1. Token layer (spring + M3 roles) — additive, no behavior change.
2. `fab-menu` component + `IFabMenuService` + `<fab-menu>` in the shell; nav
   publishes its height. Wire the simplest action (help) first.
3. Relocate dashboard actions (mode-swap, filter, beam) into contextual
   registration; strip the header trailing cluster and the moved triggers.
4. Left-handed mode + settings toggle.

Rollback: the change is frontend-only and released via the normal
version-pin/deploy flow; reverting the frontend PR restores the header controls.

## M3 References (implementation MUST consult, not reproduce from memory)

M3 is Android/Compose-first and has **no official web FAB Menu build**, so canonical
token values (springs, shape, state layers, color roles) are easy to get subtly
wrong. Before/while implementing, consult:

- **Official — M3 FAB Menu**: https://m3.material.io/components/fab-menu — component
  anatomy, states, and behavior (the authority the requirement §6 mandates).
- **M3 Expressive motion/components overview**:
  https://supercharge.design/blog/material-3-expressive
- **Discovering M3 Expressive — FAB Menu (structure/guidelines)**:
  https://medium.com/@renaud.mathieu/discovering-material-3-expressive-fab-menu-ecfae766a946
- **In-repo skills** (source of truth for the web translation): `m3-expressive-web`
  (motion/spring-motion, shape-morph, color-roles, elevation, expressive-principles),
  `modern-web-guidance` (Popover top-layer animation, `linear()` spring, anchor
  positioning), `web-design-specialist` (disclosure a11y), `cube-css` (layer/scope).

The canonical numeric values used above (spring curves/durations, state-layer
opacities, touch-target minimums, shape tokens) are transcribed from these sources;
if they conflict with the official docs at implementation time, the official docs win
and this design should be updated.

## Open Questions

- Discovery/My-Artists show a single `[help]` action — keep it as a one-item FAB
  for placement consistency, or render help as a direct button there? Deferrable:
  it does not change the service contract, the specs, or the task breakdown.
