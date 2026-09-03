## 1. Foundation — single source of design tokens

- [ ] 1.1 Create `shared/styles/` with `tokens.css`, `compositions.css`, `utilities.css`, `global.css` seeded from `src/styles/*` (fluid `clamp()` scales are canonical); unify divergent names into one set (e.g. collapse `--radius-s/m/round` and `--radius-sm/card/button` into a single radius scale)
- [ ] 1.2 Replace the too-broad `@scope(body)` with a shared wrapper scope (e.g. `.lm-ui`/audience root) and confirm `@layer` order (reset < global < composition < utility < block < exception) holds
- [ ] 1.3 Point `src/`, `admin/`, and `organizer/` entries at `shared/styles/`; delete the duplicated/diverged token blocks in `organizer/styles/main.css` and `admin/styles/main.css` and the fan-web copies now sourced from shared
- [ ] 1.4 Ensure `stylelint-plugin-cube-css` passes on `shared/styles/`; capture Storybook + Playwright screenshot baselines before any visual change lands

## 2. Shared UI primitives (`shared/ui/`)

- [ ] 2.1 Build audience-agnostic Aurelia primitives: button, card, fieldset, form-field, badge (each with default/disabled/busy states) using shared tokens
- [ ] 2.2 Build feedback/overlay primitives: dialog/sheet, toast, spinner (consistent loading/empty/error/success affordances)
- [ ] 2.3 Build navigation primitives: back-link and breadcrumb
- [ ] 2.4 Add a single `registerSharedUi(au)` helper and call it from all three `main.ts` (no per-audience registration drift)
- [ ] 2.5 Document every primitive in Storybook with its variants/states; add them to the visual-regression set
- [ ] 2.6 Verify primitives are responsive (no overflow/clipping on a mobile viewport) and accessible (keyboard-focusable, visible focus, accessible name, sufficient contrast)

## 3. Console app-shell & no-dead-end navigation

- [ ] 3.1 Build a shared console **app-shell** primitive: persistent header (home→listing, org/user context, sign-out) + breadcrumb slot + consistent page container
- [ ] 3.2 Wrap the organizer console routes in the app-shell (replace the bare `<au-viewport>`); ensure every screen shows nav + a back/breadcrumb path
- [ ] 3.3 Wrap the admin console routes in the app-shell equivalently
- [ ] 3.4 Remove dead-ends: welcome/denied/auth-callback and any created-resource status screen (e.g. lottery status) are reachable via nav/listing and offer a way back — none reachable only by URL

## 4. Migrate console screens onto shared primitives

- [ ] 4.1 Migrate organizer screens (concerts, concert-editor, lottery-phase-editor, lottery-status) to shared primitives; retire per-screen component CSS (button/badge/card/back-link/fieldset)
- [ ] 4.2 Migrate admin screens (approval-queue, approved-concerts, organizers, welcome) to shared primitives; retire per-screen component CSS
- [ ] 4.3 Confirm no console screen re-implements a role covered by the shared set

## 5. Align fan-web to the shared foundation

- [ ] 5.1 Move fan-web (`src/`) onto `shared/styles/` (brand color unchanged), reconciling scale/name drift; migrate fan-web usages of button/card/badge/etc. to the shared primitives where they match
- [ ] 5.2 Diff-review each fan-web screen against the screenshot baselines; correct any unintended visual shift

## 6. Verification & guardrails

- [ ] 6.1 `scripts/verify-bundle-isolation` passes: the fan-web consumer bundle graph contains no admin/organizer-origin module, and no shared primitive pulls console-only code into fan-web
- [ ] 6.2 Full `make lint` (biome + stylelint-cube + typecheck) and `make test` pass across all three audiences
- [ ] 6.3 Visual-regression suite (Storybook + Playwright) green; document any intentional visual changes
- [ ] 6.4 Manual pass: every console screen is reachable via nav with a way back; a created lottery phase's status is reachable from a listing (not URL-only)
