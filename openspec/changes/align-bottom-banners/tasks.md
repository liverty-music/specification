# Tasks

All tasks are in the frontend repository. Each test carries `@spec components/infrastructure/fan/web/global/<banner> "<scenario>"` for the scenarios it covers.

## 1. Shared contrast helpers

- [ ] 1.1 Move `resolveColor`, `composite`, `luminance` and `contrast` from `shared/ui/snack-bar/snack-bar.stories.ts` to `.storybook/contrast.ts` and import them from there (design D4). Verify that `npx vitest run --project=storybook --project=storybook-reduced-motion shared/ui/snack-bar` still passes 5/5 in the pinned Playwright container.

## 2. Signup prompt (global/signup-prompt-banner)

- [ ] 2.1 In `src/components/signup-prompt-banner/signup-prompt-banner.css`, set the offset to the navigation height token, the message to `--color-text-primary` at weight 500, the CTA glow to `1.2s ease-in-out 3`, and the entrance to the motion token (design D2, D3, D5). Keep the surface, which already is the shared one (D1). Verify that `npx stylelint` passes on the file.
- [ ] 2.2 Add `src/components/signup-prompt-banner/signup-prompt-banner.stories.ts` with the assertions of design D4, tagged `reduced-motion` so it runs in both storybook projects. It covers "Component renders consistently", "No dismiss control", "Banner has frosted glass background", "CTA button has glow pulse animation", "CTA button has no animation for reduced motion", "Banner message text", "Banner slides in on appearance" and "Banner appears instantly for reduced motion". Where `test/components/signup-prompt-banner.spec.ts` already verifies a scenario, annotate that test instead. Verify that the story fails on the current CSS (run it once before 2.1) and passes after it, in the pinned container.

## 3. Install banner (global/pwa-install-banner)

- [ ] 3.1 In `src/components/pwa-install-banner/pwa-install-banner.css`, replace the surface with the shared one (D1: drop the 95% base, the tint wash, the `::before` line and the `::after` bloom), set the offset to the navigation height token, drop the label's `opacity`, set the CTA glow to `1.2s ease-in-out 3`, and add the fade to the entrance (D2, D3, D5). Verify that `npx stylelint` passes on the file.
- [ ] 3.2 Add `src/components/pwa-install-banner/pwa-install-banner.stories.ts` with a mock `IPwaInstallService` registered through `items` and the assertions of design D4, tagged `reduced-motion`. It covers "PWA install prompt displays localized text", "Banner is fixed at the bottom above the nav bar", "Banner frosted glass and gradient border", "CTA button glow pulse animation", "Banner message text", "Reduced motion — no animation" and "Banner slides in on appearance". Verify that the story fails on the current CSS (run it once before 3.1) and passes after it, in the pinned container.

## 4. Stale translations

- [ ] 4.1 Delete `pwa.title`, `pwa.description`, `pwa.install` and `pwa.notNow` from `src/locales/ja/translation.json` and `src/locales/en/translation.json`, keeping `pwa.updateAvailable` and `pwa.updateAction` (design D5). Verify first that `git grep` finds none of the four keys in `src/`, `shared/`, `organizer/`, `test/` or `e2e/`, then that `make test` passes.

## 5. Integration

- [ ] 5.1 Verify that `make check` passes in frontend, that `npx playwright test e2e/functional/snack-bar.spec.ts e2e/pwa` passes (the snack's placement above each banner and the install flow are unchanged), and that `openspec validate align-bottom-banners --strict` and `python3 scripts/check-scenario-coverage.py align-bottom-banners` pass in specification once the frontend PR has merged.

## 6. Ship

- [ ] 6.1 Open the frontend PR citing `OpenSpec-Change: align-bottom-banners` and the store commit, and merge it once CI is green.
- [ ] 6.2 After the release reaches production, check on a phone that the install banner and the signup prompt look the same apart from their layout, and that each CTA glows three times and stops. Record the result here.
