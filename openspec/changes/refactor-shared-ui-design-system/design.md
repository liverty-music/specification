## Context

See proposal.md — Why. Current state (audited): three Vite entries
(`index.html`=fan-web, `admin.html`, `organizer.html`), each with its own
`main.ts`. `src/styles/` is a mature CUBE system (tokens/compositions/utilities/
global, fluid `clamp()` scales) with ~19 components; `organizer/styles/main.css`
and `admin/styles/main.css` hold **copied-then-diverged** tokens (same brand
`oklch(65% 0.28 350deg)`, but static scales and different names). `shared/` holds
only services/config/utils — **no shared UI**. Constraints that shape the design:

- **Bundle isolation (D2 of add-admin-console / organizer-console)**: the
  consumer entry graph must contain no admin/organizer module;
  `scripts/verify-bundle-isolation` enforces it positionally (chunks under
  `assets/admin/` · `assets/organizer/`). Isolation is **one-directional** —
  `shared/` consumed by all three is already the sanctioned pattern
  (shared/services, shared/config).
- **CUBE CSS investment**: custom `stylelint-plugin-cube-css` enforces the
  methodology; `@layer` order and `@scope` are used throughout.
- **Bespoke brand**: distinctive magenta/oklch identity, canvas `dna-orb`, playful
  mobile fan app vs data-dense desktop consoles.
- **Storybook** (`@aurelia/storybook`) is already present.

## Goals / Non-Goals

**Goals:**
- One source of design tokens + a shared set of Aurelia primitives consumed by
  all three audiences (satisfies the `shared-ui-design-system` spec).
- A persistent console navigation shell so no console screen is a dead end.
- Preserve bundle isolation and CUBE conformance; guard visuals with regression.

**Non-Goals:**
- Not migrating **feature** components (dna-orb, live-highway, approval-queue,
  lottery-phase-editor, …) into the shared layer — only tokens + primitives are
  shared; feature UI stays audience-local.
- Not redesigning the fan-web experience or the brand; not adding new product
  features. Per-feature flow gaps (e.g. lottery phase list/edit) are *enabled* by
  the shell here but specified/implemented under their own feature changes.
- Not adopting a third-party component library (see Decision 1).

## Decisions

### Decision 1 — Vehicle: extract a shared design system to `shared/`; reject `@material/web`

Fix the triplication by promoting the foundation to `shared/styles/` and building
brand primitives in `shared/ui/`, consumed by all three audiences. **Do not** adopt
a component library.

- **Why not `@material/web` (Z):** it imposes a Material aesthetic on a bespoke
  brand → either a two-brand product (Material consoles vs custom fan app) or
  heavy re-theming that cancels the "batteries-included" benefit; it fights the
  CUBE + custom-stylelint investment; Aurelia 2 × Lit custom elements add
  two-way-binding / form-participation / testing friction; and `@material/web`
  active development has stalled.
- **Why not console→`src/` imports (B):** would couple consoles to the fan-web
  bundle and risk pulling fan-web-only deps; the clean seam is `shared/`, which
  all three (including fan-web) import.
- **Alternative kept open (Y):** borrow Material 3 as a *design language only* —
  its shape/type/motion/elevation **scales** expressed as CUBE tokens — while
  keeping the brand color. This is optional polish layered onto the shared tokens,
  not a dependency. The `m3-expressive-web` skill informs the token model.

### Decision 2 — Token model: single source in `shared/styles/`, fluid scales win

Move tokens/compositions/utilities/global reset to `shared/styles/`. Resolve the
fan-web (fluid `clamp()`) vs console (static) drift by **standardizing on the
fluid scales** (fan-web's), and unify divergent names (`--radius-s/m/round` →
one set). All three audiences import the shared styles; the local
`organizer/`·`admin/` token blocks and the fan-web copies are deleted.
Alternative (static scales) rejected: fluid is already the more capable system
and matches responsive goals.

### Decision 3 — `shared/ui/` primitives as Aurelia components + Storybook

Author primitives (button, card, fieldset, form-field, badge, dialog/sheet,
toast, spinner, back-link, breadcrumb, and a console **app-shell**) as Aurelia 2
components under `shared/ui/`, styled with shared tokens under `@scope
(.lm-ui-*)` or a shared wrapper scope (replacing the too-broad `@scope(body)`).
Each audience `main.ts` registers the primitive set as global resources (a single
`registerSharedUi(au)` helper to avoid triple drift). Document every primitive in
Storybook (doubles as the visual-regression surface).

### Decision 4 — Console app-shell owns navigation; fan-web keeps its mobile shell

Admin and organizer render inside a shared **console app-shell** (persistent
header: home→listing, org/user context, sign-out; breadcrumb slot; consistent
page container). Fan-web keeps its own mobile shell/bottom-nav (different UX
context) but consumes the same tokens + primitives. This satisfies the
"no dead-end screens" requirement generically (e.g. lottery status becomes
reachable/returnable), independent of any single feature.

### Decision 5 — Migrate incrementally, guarded by visual regression

Foundation first, then primitives, then per-screen migration, so each step is
small and reversible. Storybook + Playwright screenshots gate visual drift
(especially when fan-web adopts the unified fluid scales).

## Risks / Trade-offs

- **Fan-web visual shift** when unifying scales/names → Mitigation: baseline
  Storybook + Playwright screenshots before migration; migrate fan-web last;
  diff-review each screen.
- **Triple global-resource registration drift** → Mitigation: one
  `registerSharedUi()` helper called by all three `main.ts`.
- **Bundle isolation regression** (a shared primitive accidentally importing
  console code) → Mitigation: keep `shared/ui` free of audience imports; keep
  `verify-bundle-isolation` green in CI on every step.
- **`@scope` refactor** (from `@scope(body)` to a wrapper scope) could change
  cascade → Mitigation: land the scope change with the token move under
  regression coverage.
- **Scope creep into feature UX** (lottery list/edit, admin flows) → Mitigation:
  Non-Goals fence it; feature gaps go to their own changes.

## Migration Plan

1. **Foundation**: create `shared/styles/` (tokens/compositions/utilities/global);
   point all three audiences at it; delete duplicated/diverged token blocks.
2. **Primitives**: build `shared/ui/` components + `registerSharedUi()`; document
   in Storybook; capture screenshot baselines.
3. **Console shell**: introduce the app-shell; wrap admin + organizer routes;
   remove dead-ends (welcome/denied/status get nav + back).
4. **Migrate consoles**: move organizer then admin screens onto shared primitives;
   retire per-screen component CSS.
5. **Align fan-web**: move fan-web to the shared foundation (color aside),
   reconciling scale/name drift under regression.
6. **Enforce**: keep `verify-bundle-isolation`, stylelint-cube, and
   visual-regression green throughout.

Rollback: each step is an independent PR; revert the offending PR — the shared
layer is additive until an audience is switched over, so partial adoption is safe.

## Open Questions

- Which Material 3 structural scales (if any) to borrow as the token basis
  (shape/type/motion/elevation) vs keeping fan-web's current scales verbatim —
  deferrable: it tunes token *values*, not the approach, specs, or task breakdown.
