## Why

The frontend's design foundation is **triplicated and drifting**: `src/styles/`
(fan-web) holds a mature CUBE token/composition/utility system, while
`organizer/styles/main.css` and `admin/styles/main.css` each keep their own
**copied-then-diverged** tokens (same brand color, but static vs fluid scales
and different names — `--radius-sm/card/button` vs `--radius-s/m/round`). There
is **no shared UI layer** (`shared/` holds only services/config/utils), so
buttons, cards, badges, back-links and page layout are re-invented per screen.
The result — confirmed by a UX audit of the organizer console — is fragmented
styling and **dead-end screens** (e.g. a lottery phase's status is reachable only
by URL; the console shell is a bare `<au-viewport>` with no persistent
navigation). This blocks organizers from using the console and will repeat with
every new console feature. A single shared design system fixes the root cause;
adopting a third-party component library (e.g. `@material/web`) would fight the
existing bespoke brand and CUBE investment instead.

## What Changes

- Introduce a **single-source UI foundation** under `shared/styles/` (design
  tokens, compositions, utilities, global reset) consumed by all three audiences
  (fan-web, admin, organizer); remove the duplicated/diverged token sets in
  `organizer/` and `admin/` (and align `src/` to the shared source).
- Introduce **`shared/ui/`**: audience-agnostic brand **primitives** as Aurelia 2
  components (button, card, fieldset, form-field, badge, dialog/sheet, toast,
  spinner, back-link, breadcrumb, and a console **app-shell** with persistent
  navigation), documented in the existing Storybook.
- Give the **admin and organizer consoles a persistent navigation shell** (home,
  org/user context, logout, breadcrumb) so **no screen is a dead-end** — every
  screen is reachable and offers a way back. Feature screens migrate onto the
  shared primitives.
- **Decision (captured in design.md): reject `@material/web` as a component
  library.** Keep the bespoke brand; optionally borrow Material 3 only as a
  *design language* (shape/type/motion/elevation scales) expressed in the shared
  CUBE tokens. Feature components (dna-orb, live-highway, approval-queue,
  lottery-phase-editor, …) stay audience-local; only primitives + tokens are
  shared.
- **Preserve bundle isolation** (the fan-web entry graph must contain no
  admin/organizer module): shared code must not pull console-only code into the
  fan-web bundle.

## Capabilities

### New Capabilities
- `shared-ui-design-system`: the cross-audience UI foundation and primitives —
  a single source of design tokens and reusable UI components shared by fan-web,
  admin, and organizer; the console persistent-navigation shell and the
  no-dead-end-screen guarantee; and the preservation of consumer/console bundle
  isolation.

### Modified Capabilities
<!-- None: this introduces a new cross-cutting capability. Per-feature flow gaps
     surfaced by the audit (e.g. lottery phase list/edit/status navigation) are
     enabled by the console shell here but specified under their own feature
     capabilities in separate changes. -->

## Impact

- **Frontend code**: `frontend/shared/` (new `styles/` + `ui/`), `frontend/src/`
  (fan-web migrates to shared foundation), `frontend/organizer/` and
  `frontend/admin/` (remove local token copies, adopt shared primitives + app
  shell, retire per-screen component CSS). Each audience `main.ts` registers the
  shared UI primitives as global resources.
- **Build/tooling**: Vite (three entries: `index.html`, `admin.html`,
  `organizer.html`) and `scripts/verify-bundle-isolation` (must still pass);
  `stylelint-plugin-cube-css` (shared styles must conform); Storybook (documents
  `shared/ui`).
- **No backend / proto / BSR impact.** Frontend-only, no API change.
- **Risk**: unifying fan-web fluid `clamp()` scales with the consoles' static
  scales can shift fan-web visuals — guard the migration with visual-regression
  (Storybook + Playwright screenshots).
