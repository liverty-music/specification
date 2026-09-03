## Context

See `proposal.md` → Why. The frontend is Aurelia 2 + Vite + CUBE CSS (`@layer reset, tokens, global,
composition, utility, block, exception`) with an oklch-only token layer in `src/styles/tokens.css` and a
Biome/stylelint gate that bans hex/hsl, physical properties, and untokenized values. Existing feedback
infrastructure to build on:

- A zero-specificity global press baseline (`:where(button:active)` → `scale(0.97)`) in `global.css`.
- The `busy-on-click` custom attribute + `[data-busy]` spinner overlay utility — the established pattern for
  attaching cross-cutting interaction behavior declaratively.
- oklch relative color (`oklch(from var(--x) l c h / n%)`) and `color-mix` already used for state feedback
  (57 and 31 sites) — but with ad-hoc opacities.
- `state-placeholder` component for empty/error states (no loading/skeleton variant yet).
- The discovery orb's `vibrate()` helper (`dna-orb-canvas.ts`) — the only haptic in the app.
- `@starting-style` already used in 3 places (proof the enter-animation primitive is viable here).

Token values referenced below (state-layer %, spring beziers, shape dp) are the M3 conceptual baseline from
the `m3-expressive-web` skill; confirm exact numbers against m3.material.io during implementation.

## Goals / Non-Goals

**Goals:**
- One shared token vocabulary (color roles, state-layer, motion spatial/effects, shape roles, surface tiers)
  layered over existing tokens without breaking current components.
- Reusable feedback primitives delivered through the project's existing extension seams (CUBE utilities,
  Aurelia custom attributes, a DI service) so screens opt in declaratively, mirroring `busy-on-click`.
- Consistent feedback across all primary screens (dashboard, my-artists, nav, filter bar, forms).

**Non-Goals:**
- No parallel palette or `--md-sys-*` hex tokens — roles are aliases in oklch (Strategy A).
- No `@material/web` / component library, no dynamic-color seed generation, no JS animation library.
- No change to routing, RPC, or data flow; feedback is presentation-layer only.

## Decisions

### D1. Token strategy: semantic aliases over existing tokens (Strategy A), not a parallel palette

M3 role tokens (`--md-sys-color-*`, state-layer, motion, shape) are defined in `@layer tokens` as `var()`
aliases onto the existing brand/surface/radius/step tokens; only genuinely missing roles (`on-*`,
`*-container`, `outline`, two extra surface tiers, `-increased` radii) get new oklch values derived via
relative color syntax. Alternative — a fresh native `--md-sys-*` palette — was rejected: it would duplicate
the palette, fight the "festival" brand identity, and force a big-bang migration. Aliasing lets components
migrate one at a time while both names resolve to the same value.

### D2. Ripple + press-morph as a custom attribute, not per-component CSS

Deliver tap feedback as a reusable Aurelia custom attribute (e.g. `press-feedback`) plus a CUBE utility,
following the `busy-on-click` precedent, so it attaches app-wide without editing every component. Ripple uses
a contact-point overlay pseudo/element positioned from the pointer coordinates; press-morph animates
`border-radius` (round↔squircle) on `:active` with a **spatial** spring token. The clickable box is never
animated (only visual shape/overlay), keeping hit area stable. Alternative — hand-written `:active` blocks
per component — rejected as unscalable and the reason feedback siloed today.

### D3. Motion tokens partitioned by property class (spatial vs effects)

Two spring families as cubic-bezier approximations: **spatial** (overshoot >1 control point, for
transform/size/radius) and **effects** (≤1, for color/opacity), plus standard/emphasized easing and a
duration scale. This encodes the single most common motion bug (bouncy opacity / flat movement) as a
token-selection decision. Scattered raw-ms values and one-off beziers (welcome's `0.34,1.56,0.64,1`,
snack-bar's `0.16,1,0.3,1`) are replaced by these tokens. WAAPI spring libs were considered for higher
fidelity but rejected for bundle cost — CSS bezier approximations cover the cases here.

### D4. Skeleton as a `state-placeholder` loading variant + utility

Add a loading/skeleton variant to the existing `state-placeholder` component and a `.skeleton` CUBE utility
(shimmer via an effects-token animation, static under reduced motion). Screens render skeleton blocks shaped
like their real content so the swap is layout-shift-free. Replaces the dashboard's `<p>loading</p>` and the
centered spinner pattern for content regions (spinners remain fine for in-flight button actions via
`busy-on-click`).

### D5. Haptic as a shared DI service, feature-detected

Generalize the orb's `vibrate()` into a `HapticService` (singleton, `DI.createInterface()` per the project's
service convention) that feature-detects `navigator.vibrate` and no-ops where absent (iOS Safari). Confirm
actions call it alongside visual feedback; it is never the sole feedback. Keeps the platform quirk in one
place instead of scattered guards.

### D6. List transitions via platform CSS (`@starting-style` + `allow-discrete`)

Use `@starting-style` and `transition-behavior: allow-discrete` for enter/exit (already proven in 3 sites),
driven by Aurelia `repeat.for`. No FLIP/JS reorder engine in this change — enter/exit covers the
follow/unfollow and content-list cases; reorder animation is deferred.

### D7. Rollout order within this change: foundation → primitives → screens → verify

Tokens land first (inert until consumed), then each primitive, then per-screen application, then a
reduced-motion / forced-colors / contrast verification pass. This keeps every intermediate state shippable
and lets `make check` gate each step.

## Risks / Trade-offs

- **Over-application of motion/haptic (feels noisy)** → Enforce the M3 expression budget (1–2 hero moments
  per flow) in the `interaction-feedback` spec; keep siblings foundational; haptic only on confirm actions.
- **Aliasing leaves two token names for the same value (confusion)** → Treat host tokens as the physical
  layer and M3 roles as the semantic layer; document the mapping in `tokens.css`; migrate consumers to roles
  opportunistically, not all at once.
- **Ripple/press-morph global attribute regresses a bespoke component** → Zero-specificity `:where()` base so
  components with their own `:active` keep precedence (same technique as today's press baseline); roll out
  screen-by-screen behind `make check`.
- **Contrast regressions from role remap on dynamic-hue cards** → The `m3-design-tokens` spec makes
  on-color/contrast a scenario; verify the artist-hue card range explicitly during rollout.
- **cubic-bezier springs are approximations, not true physics** → Acceptable for these UI-scale morphs;
  revisit WAAPI only if a specific hero moment needs real overshoot fidelity.
- **Layout shift when skeleton → content** → Skeleton blocks must mirror content dimensions; the spec makes
  no-CLS a scenario, verified with the dashboard as the reference screen.

## Migration Plan

Additive and reversible. Tokens are inert until consumed, so the token commit is safe to land alone. Each
primitive and each screen migration is an independent step gated by `make check`; rollback is reverting the
per-step commit. No data, API, or route changes — no deploy coordination beyond the normal frontend release.

## Open Questions

- Exact haptic durations per action class (tap vs confirm) — safely tunable during implementation without
  changing specs or task breakdown.
