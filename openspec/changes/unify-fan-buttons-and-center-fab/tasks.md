# Tasks

All tasks are in the frontend repository. Each test carries `@spec <capability-path> "<scenario>"` for the scenarios it covers. Capability paths below are under `components/infrastructure/fan/web/`.

## 1. Snack bar placement (global/snack-bar)

- [ ] 1.1 In `shared/ui/snack-bar/snack-bar.css`, replace `--bottom-banner-clearance` with `var(--bottom-banner-height, 0px)` and update the comment. Delete both `:root:has(...)` clearance rules in `src/styles/global.css` (design D1). Verify that `grep -rn bottom-banner-clearance src shared` returns nothing.
- [ ] 1.2 Extend `e2e/functional/snack-bar.spec.ts` and verify that it passes. It covers "No banner is visible", "Install banner dismissed", "A banner is visible" and "Same placement for every severity" (measure the snack bar's bottom against the nav's top and the banner's top), plus "CSS entry animation" and "CSS exit animation" for the up-from-bottom direction.

## 2. Shared button style (global/ui-primitives)

- [ ] 2.1 Add `src/styles/button.css` (an `@scope (.button)` block for filled, plus exception-layer `[data-variant]` rules for outlined, danger and on-container, using `color-mix()` for translucency) and import it from `main.css` (design D2). Verify that `npm run lint` (stylelint CUBE rules) passes.
- [ ] 2.2 Add `src/styles/button.stories.ts` with a Catalog story that renders all four variants as `<button>` and `<a>`, with a `toMatchScreenshot` baseline. Verify that `npm run test-storybook` passes and covers "Default variant", "Button on a coloured surface" and "Catalog matches the specification".
- [ ] 2.3 Migrate the checkout, event, lottery-entry and lottery-entry-status routes to `[ button ] [ pressable ]` with the variant mapping in design D3, deleting their `*-btn-*` rules. Verify that `rendered-screens.spec.ts` passes for those routes, and that a Playwright check in `e2e/functional` finds `data-variant="danger"` on the entry-cancel button and outlined variants on secondary actions. That check is annotated "Secondary and dismissive actions are outlined" and "Destructive action".
- [ ] 2.4 Migrate the welcome, discovery, my-artists, dashboard, tickets and settings routes, and remove `discover-cta` from `utilities.css`. Verify that `rendered-screens.spec.ts` passes for those routes and the affected Storybook screenshots are re-approved after a visual check.
- [ ] 2.5 Migrate the components (error-banner, error states, post-signup-dialog, notification-prompt, bottom-sheet footers, signup-prompt-banner and pwa-install-banner as on-container, selector and consent buttons). Verify that the 44 class names listed in the plan no longer appear (`grep -rnoE 'class="[^"]*(btn|cta)' src shared` lists only `[ button ]` usages and icon-only buttons), and that `npm test` and `npm run test-storybook` pass.

## 3. Update action (global/snack-bar)

- [ ] 3.1 Add an optional `icon` to `SnackOptions`, used instead of the severity icon. Render the action as `[ button ]` with `data-variant="on-container"`. Add a `data-attention` glow that runs 3 iterations and is disabled under reduced motion. In `src/main.ts`, pass `icon: 'rotate-ccw'` and the attention flag for the update snack (design D4). Verify with a unit test in `snack-bar.spec.ts` that a custom icon overrides the severity icon.
- [ ] 3.2 Add an `UpdateAction` story to `shared/ui/snack-bar/snack-bar.stories.ts` (with a screenshot) and verify that it passes in both Storybook projects (normal and reduced motion). It covers "Action button appears in the on-container style" (border width ≥ 1.5px, radius 12px), "The glow plays three times, then stops" (`animation-iteration-count` 3), "Animation is suppressed under reduced motion" and "Leading icon depicts a refresh".

## 4. Navigation and the Settings entry (global/bottom-nav-bar, global/page-header, route/settings)

- [ ] 4.1 Set `nav: false` on the Settings route in `src/app-shell.ts`. Lay out `bottom-nav-bar` as a five-column grid with a fixed centre slot, and add the `data-notch` exception mask bound to `fabMenu.actions.length > 0` (design D5). Verify with a Playwright test annotated "Navigation shown on post-onboarding routes", "Route with FAB actions", "Route without FAB actions", "Tabs do not move between routes", "Route outside every tab" and "Tab route displayed" that passes on Chromium and WebKit.
- [ ] 4.2 Add a `show-settings` bindable to `page-header` that renders the gear link after the slot, and bind it in `app-shell.html` from "displayed route is a `nav: true` route" (design D6). Verify with a page-header story (screenshot) and a Playwright test annotated "Gear on a tab page", "No gear on Settings", "No gear outside the tabs" and "Gear after a route's own trailing content".
- [ ] 4.3 Verify that the existing Settings header test still passes, and annotate it "Header reads \"Settings\" regardless of active locale" and "Header shares the navigation tab label source".

## 5. FAB (global/fab-menu)

- [ ] 5.1 Fix the open-state bug: set `isOpen = false` in `FabMenu.detaching()` (design D10). Verify with a unit test in `fab-menu.spec.ts` (detach while open, then reattach, and `isOpen` is false) and a Playwright test annotated "Leaving with the arc open and coming back" and "Moving between two routes that both contribute actions".
- [ ] 5.2 Add the FAB tokens to `tokens.css`. Centre the toggle on the nav's top edge and fill it with the brand gradient and glow. Replace the `+` with the inline equalizer and `×` SVGs at `--fab-icon-size` (2rem), with a one-shot bar bounce on open (design D7, D9). Verify with a Playwright test annotated "Launcher present with the navigation bar", "FAB floats in the thumb zone above content", "Tapping the FAB expands the action list", "Tapping again collapses the list" and "Idle glyph is still".
- [ ] 5.3 Lay out the panel items along the `offset-path` thumb arc with `--i`/`--n` bindings, labels on the outer side, and staggered spring travel from the FAB (design D7). Verify with a Playwright test at 320px and 390px viewports annotated "Every item shows icon and label", "Labels never overlap icons" (no label box intersects another item; every item is 16px or more inside the edges, with the dashboard's four actions), "Items are comfortably tappable", "Expansion uses spring motion", "Reduced motion lands the end state without bounce" and "Expanded panel keeps strong contrast". Also verify that the existing `fab-menu-beam-toggle.spec.ts` still passes.
- [ ] 5.4 Mirror the arc path and label side under `[data-handed="left"]`, keeping the FAB centred. Update `settings.leftHandedDesc` in `src/locales/ja` and `src/locales/en` (for example 「アクションメニューを左手側に開きます」). Verify with a Playwright test annotated "Default arc curves to the right", "Left-handed mode mirrors the arc" and "Preference persists across sessions".
- [ ] 5.5 Add `:root:has(.snack-item:popover-open) { --fab-sunk: 1 }` to `global.css`, and the sunk scale and translate to `fab-menu.css` (design D8). Verify with a Playwright test that publishes a snack through `__lm_publishSnack`, annotated "A snack bar opens" (40px; the FAB's top is at or below the nav's top; no overlap with the snack bar), "The sunk FAB still opens the actions" and "The last snack bar closes".
- [ ] 5.6 Add `e2e/functional/fab-menu-top-layer.spec.ts`, annotated "FAB stays above the Discovery dna orb" (the toggle matches `:popover-open`, and `elementFromPoint` at its centre resolves inside the toggle), "FAB hidden when navigation is hidden" and "FAB hidden when no actions are contributed". Verify that it passes on Chromium and WebKit.

## 6. Integration and release

- [ ] 6.1 Verify that `make check` passes in frontend and that `openspec validate unify-fan-buttons-and-center-fab --strict` passes in specification.
- [ ] 6.2 Open the frontend PR citing `OpenSpec-Change: unify-fan-buttons-and-center-fab` and the store commit, and merge it once CI is green.
- [ ] 6.3 After the production rollout, verify on a phone in production and record the result here. Check the snack bar placement after a second deploy triggers the update snack, the notch and four tabs, the gear, the thumb arc with the dashboard's four actions, the sink while the update snack is open, and the collapsed FAB after moving Home → Tickets → Home.
