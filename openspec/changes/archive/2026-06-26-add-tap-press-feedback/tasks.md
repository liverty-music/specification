## 1. Implementation (frontend, branch `claude/ui-feedback-tap-effects-wtcgzt`)

- [x] 1.1 `src/styles/global.css`: add `:where(button):active:not(:disabled)` scale baseline + add `transform` to the `:where(button)` transition list
- [x] 1.2 `src/styles/global.css`: add `prefers-reduced-motion: reduce` fallback for the button baseline (drop scale, keep a non-motion cue)
- [x] 1.3 `src/components/bottom-nav-bar/bottom-nav-bar.css`: add `.nav-tab:active` press cue + `transform` transition, distinct from the persistent selected state
- [x] 1.4 `src/components/bottom-nav-bar/bottom-nav-bar.css`: add `prefers-reduced-motion` fallback for `.nav-tab` (accent-tinted background)
- [x] 1.5 `src/styles/utilities.css`: add `.discover-cta:active` press cue (scale + ~50ms ease-in) + `prefers-reduced-motion` fallback — the anchor-based primary CTA the button baseline cannot reach
- [x] 1.6 `src/routes/settings/settings-route.css`: add `.settings-row:active` background-deepen with `transform: none` to suppress the global scale

## 2. Local checks

- [x] 2.1 Run `make lint` (Biome + stylelint + typecheck) — green
- [x] 2.2 Run the `brand-vocabulary` check — green
- [x] 2.3 Confirm `@layer block` components with existing `:active` are visually unchanged (no cascade regression)

## 3. Ship

- [x] 3.1 Open the frontend PR (Conventional Commit, body explains why, `Refs: #470`); merge after CI is green
- [x] 3.2 Cut the frontend GitHub Release → AR retag → automated prod pin bump → ArgoCD sync
- [x] 3.3 Verify the press feedback live on prod (`dashboard` CTA + bottom-nav)
- [x] 3.4 Archive this OpenSpec change once shipped and verified
