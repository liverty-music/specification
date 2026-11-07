# Tasks

Each numbered group is one frontend PR citing this change, released and checked in production before the next group starts (design "Delivery"). `make check` and `npm run test-storybook` must pass for every group. Regenerate visual baselines with the `visual-baselines` skill wherever a group changes a storied component's look.

## 1. Lint enforces the layers (no visible change)

- [ ] 1.1 Upgrade to `stylelint` 18 and `stylelint-config-standard` 41, and fix whatever the 18.0.0 migration guide requires; verify `npm run lint:css` and the `stylelint-plugin-cube-css/test` suite pass with no rule changes yet.
- [ ] 1.2 Replace `stylelint-use-logical` with `property-layout-mappings` (keeping the `width`/`height` exception) and uninstall it; replace `cube/no-undefined-color-token` with `no-unknown-custom-properties` and `referenceFiles`, and delete the rule and its test; drop `at-rule-no-unknown` entries core now knows; verify lint reports nothing new on the current code.
- [ ] 1.3 Run the two spikes in design "Core stylelint rules": try `value-type-custom-property-required-list` against `cube/require-token-variables`' test cases, and check `no-unknown-custom-properties` for false positives across components. Apply each stated fallback if needed, and record the outcome in design.md.
- [ ] 1.4 Add the component-stylesheet `overrides` from the design table and the three disable-reporting options; lower `cube/block-max-lines` to 100; verify with a new suite in `stylelint-plugin-cube-css/test/` that runs the real `stylelint.config.js` over fixtures: a `margin: 0` list inside `.flow`, `padding: 0`, `list-style: none`, `font-family`, `outline`, a raw `box-shadow`, an unknown token, and a disable comment with no reason each fail, and a clean block passes.
- [ ] 1.5 Generate and commit `stylelint-suppressions.json` with `--suppress`; verify `npm run lint:css` passes and that adding a new `margin` to a suppressed file fails.
- [ ] 1.6 Update `AGENTS.md` ("CSS rules live in `stylelint.config.js`"): how to read the suppression list, that a disable needs a reason, and the breakpoints review criterion; verify `test/` documentation checks pass.

## 2. Shared tokens beside the old ones (no visible change)

- [ ] 2.1 Add to `shared/styles/`: type styles and tracking, the plain typeface, elevation levels, focus ring size, target size, and the `.md-typescale-*` utilities with the one `cube/utility-single-property` allowance; import them in `src/styles/main.css`, `organizer/styles/main.css` and `organizer/styles/shared.css`. Verify with a `Foundations/*` story covering "Title at any window width", "Emphasized style is one step heavier" and "Larger browser text size" in both apps, and "A floating surface at a named level". Annotate `@spec` under both design-tokens capabilities.
- [ ] 2.2 Add `--md-sys-color-*`, `--md-sys-shape-corner-*` (at the Material 3 values), `--md-ref-typeface-brand` and spring tokens per app, aliasing today's tokens where colours are unchanged; verify `npm run lint:css` and that every existing story's pixels are unchanged.

## 3. Mechanical renames (no visible change)

- [ ] 3.1 Rename colour tokens to `--md-sys-color-*` in the fan app and the organizer console, one scripted commit, using the mapping in design "Token names". Merge `--color-text-muted` into `on-surface-variant` as a separate commit, and verify contrast through the story a11y run and the design-tokens "No undefined color" scenario (`@spec`).
- [ ] 3.2 Rename shape, state, motion and spring tokens in separate scripted commits; delete `--fab-state-*`, `--transition-*` and the unused `--container-*`. Replace `--radius-sheet` at 24 px with extra-large at 28 px as its own commit, and verify the "Radius matches component size" and "Directional rounding is RTL-safe" scenarios and regenerated baselines.
- [ ] 3.3 Verify the scenarios in design-tokens "State and motion tokens are shared with the organizer console" with a test that reads both apps' computed values, and annotate `@spec`.

## 4. Type styles and typefaces (visible)

- [ ] 4.1 Change `index.html` to load Righteous and Noto Sans JP, and remove Poppins and Outfit. Set `font-synthesis-weight: none` and the typeface tokens. Before merging, record `/dashboard` LCP and transferred font bytes; verify after release against the 200 ms threshold in design "Risks". Cover "Japanese text looks the same on every device", "Japanese in a headline" and "Offline" with a Playwright test that asserts the rendered font, blocks the font request for the offline case, and runs on the Pixel 7 and iPhone device profiles.
- [ ] 4.2 Move body text to the body-large default and give every fan heading and text a type style from the mapping in design "Type styles are utility classes", route by route, removing `font-*` and `line-height` from blocks and their suppression entries; delete `--step-*`, `--leading-*` and `--font-*` from `tokens.css` at the end. Verify "Same role, same look" and "Heading level does not decide the look" by story, then run in Playwright against a local build: `/dashboard`, `/discovery`, `/my-artists`, `/tickets`, `/settings`, `/checkout`, each at 320 px and 412 px.
- [ ] 4.3 Load Noto Sans JP in `organizer.html` and copy the same stack into `organizer/guide/guide.html`; move the organizer console from `--md-type-*` to the shared type styles, removing the local definitions and the font declarations in its component stylesheets (the two monospaced values move to the `.typeface-mono` utility), and leaving body-medium as its default. Record the concerts screen's LCP and font bytes before merging and verify after release against the 200 ms threshold. Verify "Same size on PC and phone", "Counts line up", "Same typeface on Windows and on a Mac" and "Font cannot be loaded" (`@spec`) with a Playwright test that asserts the rendered font and blocks the font request, run `test/organizer/guide.spec.ts`, and run the concerts and sales screens in Playwright at 390 px and 1440 px in light and dark.
- [ ] 4.4 Update the live-highway stage headers and page-header, page-help and toast styling to the roles in their deltas, keeping the artist name's container-relative size behind a described disable; annotate those scenarios and run `/dashboard` in Playwright to confirm headers stay readable on all three stage colours.

## 5. Spacing and margins (visible)

- [ ] 5.1 Fix `--space-*` in `src/styles/tokens.css` at 4, 8, 12, 16, 24, 32, 48, 64 and 96 px, matching the organizer's values on the shared steps; verify "Same spacing on any width" for both apps by story.
- [ ] 5.2 Remove the declarations that repeat `reset.css` (108) with a scripted commit; verify the suppression list shrinks by that count, every story passes, and pixel changes appear only where a composition was being cancelled. Re-check each changed baseline by eye.
- [ ] 5.3 Replace the fan app's 118 and the organizer console's 45 margin declarations with `flow`, `stack`, `gap` or padding on the parent, a file at a time; add a composition to `compositions.css` only when two blocks need the same layout. Verify the suppression list has no `margin` entries, and run in Playwright on a local build the screens with the most margins: `/`, `/settings`, the help sheet and the home selector at 320 px and 412 px.

## 6. Focus, touch targets and elevation (visible)

- [ ] 6.1 Add the global focus ring to the fan app's `src/styles/global.css` and remove the 13 stylesheets' own outlines; move the organizer ring to the shared size tokens, keeping its three fields behind described disables. Verify "Tabbing through a screen" and "Pointer click" in both apps with Playwright keyboard runs, including 3:1 against each surface tier.
- [ ] 6.2 Raise the fan app's controls to 48 × 48 px per design "48 px targets": the default text button, the 15 controls at 44 px, the hype dots, the date tabs and chips. Verify with a story helper that measures each control's target in every changed story ("Compact button", "Neighbouring controls"), and the My Artists Widths story at 320 px. Update and annotate the my-artists, welcome, dashboard, event-detail-sheet and app-shell scenarios, and raise the organizer's 40 px `console-button` and 32 px `top-app-bar` buttons to meet their existing action-feedback spec.
- [ ] 6.3 Replace the fan app's raw `box-shadow` values with elevation levels or `--glow-*`, keeping the spec-defined hype glows behind a described disable, and replace the organizer console's two inset field outlines with a border; verify the suppression list has no `box-shadow` entries and "Resting depth uses a tonal tier" still holds.
- [ ] 6.4 Add the `prefers-contrast: more` colour values in both apps; verify "Secondary text with more contrast" and "Regular contrast is unchanged" with a Storybook project or story that emulates the media feature and measures the ratios.

## 7. Shared fan components (visible)

- [ ] 7.1 Add the `heading` bindable to `<bottom-sheet>` with the Material 3 sheet values; move all 12 sheets to it, removing their title classes and `aria-labelledby` ids. Verify "Sheet with a heading", "Space below the heading", "Sheet without a heading", "Handle bar rendering" and "Sheet body structure" by story, and open the All Nearby filter sheet in Storybook at 320 px, which is where this change started.
- [ ] 7.2 Add `src/components/list-item/` and move the settings rows and the All Nearby filter rows to it; verify "Settings row and filter row match", "Long value" and "Row with two lines" by story, and run `/settings` and the filter sheet in Playwright. Run `npm run build && npm run verify:build-templates` and update `ROUTE_MARKERS` if a marker class moved.
- [ ] 7.3 Move `<svg-icon>` to the sm, md, lg and xl sizes and remove xs; set icons that stand alone to lg, replacing the sizes in component stylesheets. Verify the "Size variants" scenario by story, and that no icon shrinks below 16 px in the changed baselines.
- [ ] 7.4 Set the navigation bar to 64 px with 24 px icons and label-medium labels, keeping the FAB notch and the snack bar clearance aligned; verify "Bar height" and "Bar on a phone with a home indicator" by story, and run `/dashboard` and `/discovery` in Playwright on the Pixel 7 and iPhone profiles with the FAB and a snack showing.

## 8. Blocks under 100 lines (visible only by accident)

- [ ] 8.1 Move shared rules out of the 32 fan stylesheets over the limit, then split each into components, largest first (`discovery-route`, `welcome-route`, `fab-menu`, `concert-highway`, `my-artists-route`, `settings-list`, `order-route`, `event-detail-sheet`); verify no entry for `cube/block-max-lines` remains for a file and that its stories' pixels are unchanged. Add a named story for any new component with a visual state, as `AGENTS.md` requires.
- [ ] 8.2 Do the same for the 8 organizer stylesheets (`top-app-bar`, `concert-editor-route`, `concert-route`, `venue-field`, `console-field`, `sales-tab`, `organizer-shell`, `console-button`); verify as in 8.1, and check whether the organizer guide (`organizer/guide/guide.html`) quotes anything that moved, running `test/organizer/guide.spec.ts`.
- [ ] 8.3 For any block left over 100 lines, write the reason in a described disable and list it in design.md; verify `stylelint-suppressions.json` has no `cube/block-max-lines` entries.

## 9. Close out

- [ ] 9.1 Annotate or add tests for every scenario `python3 scripts/check-scenario-coverage.py adopt-m3-cube-ui-foundation` still reports, mainly `bottom-sheet` and `live-highway`; verify it exits 0.
- [ ] 9.2 Delete `stylelint-suppressions.json` and any token still aliased for migration; verify `npm run lint:css` passes with no suppressions file and `grep` finds no `--step-`, `--leading-`, `--font-`, `--radius-`, `--shadow-` or `--md-type-` in `src/`, `shared/` and `organizer/`.
- [ ] 9.3 Verify in production after the last release: open `/dashboard`, `/discovery`, `/my-artists`, `/tickets`, `/settings` and the organizer concerts screen in Playwright with the Pixel 7 and iPhone profiles, check no horizontal scroll and no clipped text, and read the rollout status; note what was checked by emulation rather than on a physical device.
