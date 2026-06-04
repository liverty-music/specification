## 1. Layout implementation (CSS)

- [ ] 1.1 In `event-detail-sheet.css`, change `.journey-outcome` from `flex-direction: column` to a horizontal row holding the win route and lose route side by side
- [ ] 1.2 Flatten `.journey-route-success` to lay `unpaid › paid` horizontally instead of stacked
- [ ] 1.3 Remove the bordered-card chrome (`border` + `padding`) from `.journey-route`; introduce a lightweight separator between the win and lose routes and keep `data-dimmed` route dimming
- [ ] 1.4 Allow the outcome row to `flex-wrap` so a narrow (~360px) viewport wraps instead of overflowing; keep node `flex: 1 1 auto` and the 44px (`min-block-size: 2.75rem`) tap target intact
- [ ] 1.5 Give `.journey-arrow` dedicated `margin-inline` (≈`--space-2xs`) independent of the container gap, and raise the glyph size to ~`--step-0` so it is not hairline
- [ ] 1.6 Remove the `.journey-arrow-down` rule (vertical `↓`); both phases now use the horizontal `›`

## 2. Template cleanup

- [ ] 2.1 In `event-detail-sheet.html`, remove the `journey-arrow-down` modifier from the win-route connector so it renders the horizontal `›`
- [ ] 2.2 Confirm the DOM structure, radiogroup roles, `data-testid` hooks, and `keydown.trigger="onJourneyKeydown"` binding are unchanged

## 3. Behavior & accessibility verification

- [ ] 3.1 Verify radiogroup keyboard navigation still traverses all five nodes in the new horizontal arrangement (Left/Right and Up/Down); adjust `onJourneyKeydown` only if a direction regresses
- [ ] 3.2 Measure the control's vertical footprint and confirm it is ~half the prior height on a mobile viewport
- [ ] 3.3 Confirm each node still shows the canonical label/icon/hue and that win/lose routes stay visually distinguishable

## 4. Tests & checks

- [ ] 4.1 Run `make check` (lint + unit) in `frontend` and fix any failures
- [ ] 4.2 Update/confirm component and Playwright E2E tests for the journey control (`journey-btn`, `journey-remove-btn`) still pass; E2E mocks the RPC (dev env is intentionally stopped — mock, do not proxy)
- [ ] 4.3 Regenerate frontend visual baselines for the changed sheet (intentional UI change blocks merge until the visual-baselines CI artifact is deleted to force regen)

## 5. Ship

- [ ] 5.1 Open the frontend PR (commit with `Refs: #<issue>`; body explains the why) and drive CI to green
- [ ] 5.2 Merge to `main` after all CI checks pass and review comments are resolved
- [ ] 5.3 Cut the frontend prod release (GH Release retag → prod AR; automated repository_dispatch bumps the cloud-provisioning prod pin → ArgoCD auto-sync) and confirm the change is live in prod
