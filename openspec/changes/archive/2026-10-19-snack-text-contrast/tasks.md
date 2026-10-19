# Tasks

All tasks are in the frontend repository. Each test carries `@spec components/infrastructure/fan/web/global/snack-bar "<scenario>"` for the scenarios it covers.

## 1. Snack container contrast (global/snack-bar)

- [x] 1.1 In `shared/ui/snack-bar/snack-bar.css`, set the info stops to `oklch(from var(--color-brand-primary) 51.5% c h)` and `oklch(from var(--color-brand-secondary) 49% c h)`, and the warning stops to `oklch(47.5% 0.16 75deg)`, with a comment that states the 4.5:1 reason (design D1). Leave the error stops, the brand tokens and `--snack-bar-container` unchanged. Verify that `npx stylelint shared/ui/snack-bar/snack-bar.css` passes and that `git diff src/styles/tokens.css` is empty.
- [x] 1.2 In `shared/ui/snack-bar/snack-bar.stories.ts`, add the WCAG contrast check from design D2 to the severity stories and to UpdateAction: white text against both container stops, and the action label against its translucent fill over both stops, each at least 4.5. Annotate it with "Message contrast on every severity", "Action contrast on every severity" and "Snack severity visual variants". Regenerate the changed screenshot baselines in the pinned Playwright container. Verify that `npx vitest run --project=storybook --project=storybook-reduced-motion shared/ui/snack-bar` passes in that container, and that the check fails on the current colours (run it once before 1.1).
- [x] 1.3 Verify that `make check` passes in frontend and that `openspec validate snack-text-contrast --strict` passes in specification.
- [x] 1.4 Sample the contrast check along each gradient (every 5%, in oklab) instead of at the two ends, and lower the info stops to 50.5% and 48%, the highest at which the action keeps 4.5:1 mid-way (design D1). Verify that the snack-bar stories pass in the pinned container and that `make check` passes.

## 2. Ship

- [x] 2.1 Open the frontend PR citing `OpenSpec-Change: snack-text-contrast` and the store commit, and merge it once CI is green.
- [x] 2.2 After the release reaches production, check on a phone that the update snack and a warning snack look as compared in Storybook, and record the result here.
  - 2026-10-19: v1.105.1 is live in prod (`fan-web:v1.105.1`, served CSS carries the 50.5% / 48% info stops and the 47.5% warning stop). The owner checked the update snack and a warning snack on a phone: they look as compared in Storybook.
