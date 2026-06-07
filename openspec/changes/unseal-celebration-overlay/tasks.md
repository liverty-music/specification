## 1. Implement the text-lens backdrop

- [x] 1.1 In `frontend/src/components/celebration-overlay/celebration-overlay.css`, lower the `.celebration-overlay` scrim from `oklch(0% 0 0deg / 80%)` to a light value (~`/18%`) and remove the full-screen `backdrop-filter: blur(8px)`
- [x] 1.2 Add a `.celebration-overlay::before` feathered radial "text-lens" (dark gradient sized to the text group) layered with the existing brand-purple glow halo, using design tokens / relative color syntax per CUBE CSS
- [x] 1.3 Strengthen `.celebration-text` shadow and add a thin dark outline (multi-stop `text-shadow`) to `.celebration-sub-text` as a legibility floor
- [x] 1.4 Confirm tiers, gating, confetti, tap-to-dismiss, and the `prefers-reduced-motion` block are untouched (backdrop-only diff)

## 2. Verify appearance and legibility

- [x] 2.1 Render the overlay over a vibrant timetable and over the worst-case bright cards (near-stage cyan / accent green / amber); confirm edges stay colorful and both text lines are legible
- [x] 2.2 Confirm `prefers-reduced-motion: reduce` still disables confetti and transitions (block untouched by this change)
- [x] 2.3 Update/extend `frontend/src/components/celebration-overlay/celebration-overlay.spec.ts` if a backdrop/contrast assertion is warranted — N/A: spec is a ViewModel-only unit test; backdrop is covered by visual baselines (3.2)

## 3. Quality gate

- [x] 3.1 Run `make check` in `frontend/` (Biome + stylelint + typecheck + unit tests) and fix any findings — green (113 files / 1252 tests passed)
- [ ] 3.2 Regenerate frontend visual baselines for the celebration overlay (intentional UI change) per the project baseline-refresh process — release-time CI action (delete visual-baselines artifacts to force regen)

## 4. Ship to production

- [ ] 4.1 Open the frontend PR (commit per Liverty convention with `Refs: #<issue>`), get CI green, address review, merge to `main`
- [ ] 4.2 Cut the frontend GitHub Release (retag → prod AR); the automated repository_dispatch pin-bump updates cloud-provisioning and ArgoCD auto-syncs
- [ ] 4.3 Verify in production directly (no dev env): on the live app, trigger the celebration and confirm the timetable shows through with legible text
