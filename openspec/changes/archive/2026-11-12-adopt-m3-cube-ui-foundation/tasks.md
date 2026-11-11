# Tasks

Each numbered group is one frontend PR citing this change, released and checked in production before the next group starts (design "Delivery"). `make check` and `npm run test-storybook` must pass for every group. Regenerate visual baselines with the `visual-baselines` skill wherever a group changes a storied component's look.

## 1. Lint enforces the layers (no visible change)

- [x] 1.1 Upgrade to `stylelint` 18 and `stylelint-config-standard` 41, and fix whatever the 18.0.0 migration guide requires; verify `npm run lint:css` and the `stylelint-plugin-cube-css/test` suite pass with no rule changes yet.
- [x] 1.2 Replace `stylelint-use-logical` with `property-layout-mappings` (keeping the `width`/`height` exception) and uninstall it; replace `cube/no-undefined-color-token` with `no-unknown-custom-properties` and `referenceFiles`, and delete the rule and its test; drop `at-rule-no-unknown` entries core now knows; verify lint reports nothing new on the current code.
- [x] 1.3 Run the two spikes in design "Core stylelint rules": try `value-type-custom-property-required-list` against `cube/require-token-variables`' test cases, and check `no-unknown-custom-properties` for false positives across components. Apply each stated fallback if needed, and record the outcome in design.md.
- [x] 1.4 Add the component-stylesheet `overrides` from the design table and the three disable-reporting options; lower `cube/block-max-lines` to 100; verify with a new suite in `stylelint-plugin-cube-css/test/` that runs the real `stylelint.config.js` over fixtures: a `margin: 0` list inside `.flow`, `padding: 0`, `list-style: none`, `font-family`, `outline`, a raw `box-shadow`, an unknown token, and a disable comment with no reason each fail, and a clean block passes.
- [x] 1.5 Generate and commit `stylelint-suppressions.json` with `--suppress`; verify `npm run lint:css` passes and that adding a new `margin` to a suppressed file fails.
- [x] 1.6 Update `AGENTS.md` ("CSS rules live in `stylelint.config.js`"): how to read the suppression list, that a disable needs a reason, and the breakpoints review criterion; verify `test/` documentation checks pass.

## 2. Shared tokens beside the old ones (no visible change)

- [x] 2.1 Add to `shared/styles/`: type styles and tracking, the plain typeface, elevation levels, focus ring size, target size, and the `.md-typescale-*` utilities with the one `cube/utility-single-property` allowance; import them in `src/styles/main.css`, `organizer/styles/main.css` and `organizer/styles/shared.css`. Verify with a `Foundations/*` story covering "Title at any window width", "Emphasized style is one step heavier" and "Larger browser text size" in both apps, and "A floating surface at a named level". Annotate `@spec` under both design-tokens capabilities.
- [x] 2.2 Add `--md-sys-color-*`, `--md-sys-shape-corner-*` (at the Material 3 values), `--md-ref-typeface-brand` and spring tokens per app, aliasing today's tokens where colours are unchanged; verify `npm run lint:css` and that every existing story's pixels are unchanged.

## 3. Mechanical renames (no visible change)

- [x] 3.1 Rename colour tokens to `--md-sys-color-*` in the fan app and the organizer console, one scripted commit, using the mapping in design "Token names". Merge `--color-text-muted` into `on-surface-variant` as a separate commit, and verify contrast through the story a11y run and the design-tokens "No undefined color" scenario (`@spec`).
- [x] 3.2 Rename shape, state, motion and spring tokens in separate scripted commits; delete `--fab-state-*`, `--transition-*` and the unused `--container-*`. Replace `--radius-sheet` at 24 px with extra-large at 28 px as its own commit, and verify the "Radius matches component size" and "Directional rounding is RTL-safe" scenarios and regenerated baselines.
- [x] 3.3 Verify the scenarios in design-tokens "State and motion tokens are shared with the organizer console" with a test that reads both apps' computed values, and annotate `@spec`.

## 4. Type styles and typefaces (visible)

- [x] 4.1 Change `index.html` to load Righteous and Noto Sans JP, and remove Poppins and Outfit. Set `font-synthesis-weight: none` and the typeface tokens. Before merging, record `/dashboard` LCP and transferred font bytes; verify after release against the 200 ms threshold in design "Risks". Cover "Japanese text looks the same on every device", "Japanese in a headline" and "Offline" with a Playwright test that asserts the rendered font, blocks the font request for the offline case, and runs on the Pixel 7 and iPhone device profiles.
- [x] 4.2 Move body text to the body-large default and give every fan heading and text a type style from the mapping in design "Type styles are utility classes", route by route, removing `font-*` and `line-height` from blocks and their suppression entries; delete `--step-*`, `--leading-*` and `--font-*` from `tokens.css` at the end. Verify "Same role, same look" and "Heading level does not decide the look" by story, then run in Playwright against a local build: `/dashboard`, `/discovery`, `/my-artists`, `/tickets`, `/settings`, `/checkout`, each at 320 px and 412 px.
- [x] 4.3 Load Noto Sans JP in `organizer.html` and copy the same stack into `organizer/guide/guide.html`; move the organizer console from `--md-type-*` to the shared type styles, removing the local definitions and the font declarations in its component stylesheets (the two monospaced values move to the `.typeface-mono` utility), and leaving body-medium as its default. Record the concerts screen's LCP and font bytes before merging and verify after release against the 200 ms threshold. Verify "Same size on PC and phone", "Same typeface on Windows and on a Mac" and "Font cannot be loaded" (`@spec`) with a Playwright test that asserts the rendered font and blocks the font request, and "Counts line up" in the data-list Table story, where the counts render, run `test/organizer/guide.spec.ts`, and run the concerts and sales screens in Playwright at 390 px and 1440 px in light and dark.
- [x] 4.4 Update the live-highway stage headers and page-header, page-help and toast styling to the roles in their deltas, keeping the artist name's container-relative size behind a described disable; annotate those scenarios and run `/dashboard` in Playwright to confirm headers stay readable on all three stage colours.

## 5. Spacing and margins (visible)

- [x] 5.1 Fix `--space-*` in `src/styles/tokens.css` at 4, 8, 12, 16, 24, 32, 48, 64 and 96 px, matching the organizer's values on the shared steps; verify "Same spacing on any width" for both apps by story. Then annotate the page-header Default story with page-header "Visual consistency across routes" and assert its padding is exactly 12 px (group 4 left the annotation out while the padding was still fluid).
- [x] 5.2 Remove the declarations that repeat `reset.css` (108) with a scripted commit; verify the suppression list shrinks by that count, every story passes, and pixel changes appear only where a composition was being cancelled. Re-check each changed baseline by eye.
- [x] 5.3 Replace the fan app's 118 and the organizer console's 45 margin declarations with `flow`, `stack`, `gap` or padding on the parent, a file at a time; add a composition to `compositions.css` only when two blocks need the same layout. Verify the suppression list has no `margin` entries, and run in Playwright on a local build the screens with the most margins: `/`, `/settings`, the help sheet and the home selector at 320 px and 412 px.

## 6. Focus, touch targets and elevation (visible)

- [x] 6.1 Add the global focus ring to the fan app's `src/styles/global.css` and remove the 13 stylesheets' own outlines; move the organizer ring to the shared size tokens, keeping its three fields behind described disables. Verify "Tabbing through a screen" and "Pointer click" in both apps with Playwright keyboard runs, including 3:1 against each surface tier.
- [x] 6.2 Raise the fan app's controls to 48 × 48 px per design "48 px targets": the default text button, the 15 controls at 44 px, the hype dots, the date tabs and chips. Verify with a story helper that measures each control's target in every changed story ("Compact button", "Neighbouring controls"), and the My Artists Widths story at 320 px. Update and annotate the my-artists, welcome, dashboard, event-detail-sheet and app-shell scenarios, and check that the organizer's 40 px `console-button` and 32 px `top-app-bar` buttons meet their existing action-feedback spec (they do, through the `touch-target` utility, so they keep their Material 3 sizes). The default text button takes Material 3's small button: 40 px tall with a 48 px `::after` target.
- [x] 6.3 Replace the fan app's raw `box-shadow` values with elevation levels or `--glow-*`, keeping the spec-defined hype glows behind a described disable, and replace the organizer console's two inset field outlines with a border; verify the suppression list has no `box-shadow` entries and "Resting depth uses a tonal tier" still holds.
- [x] 6.4 Add the `prefers-contrast: more` colour values in both apps; verify "Secondary text with more contrast" and "Regular contrast is unchanged" with a Storybook project or story that emulates the media feature and measures the ratios.

## 7. Shared fan components (visible)

- [x] 7.1 Add the `heading` bindable to `<bottom-sheet>` with the Material 3 sheet values; move all 12 sheets to it, removing their title classes and `aria-labelledby` ids. Verify "Sheet with a heading", "Space below the heading", "Sheet without a heading", "Handle bar rendering" and "Sheet body structure" by story, and open the All Nearby filter sheet in Storybook at 320 px, which is where this change started.
- [x] 7.2 Add `src/components/list-item/` and move the settings rows and the All Nearby filter rows to it; verify "Settings row and filter row match", "Long value" and "Row with two lines" by story, and run `/settings` and the filter sheet in Playwright. Run `npm run build && npm run verify:build-templates` and update `ROUTE_MARKERS` if a marker class moved.
- [x] 7.3 Move `<svg-icon>` to the sm, md, lg and xl sizes and remove xs; set icons that stand alone to lg, replacing the sizes in component stylesheets. Verify the "Size variants" scenario by story, and that no icon shrinks below 16 px in the changed baselines.
- [x] 7.4 Set the navigation bar to 64 px with 24 px icons and label-medium labels, keeping the FAB notch and the snack bar clearance aligned; verify "Bar height" and "Bar on a phone with a home indicator" by story, and run `/dashboard` and `/discovery` in Playwright on the Pixel 7 and iPhone profiles with the FAB and a snack showing.

## 8. Blocks under 100 lines (visible only by accident)

- [x] 8.1 Move shared rules out of the 32 fan stylesheets over the limit, then split each into components, largest first (`discovery-route`, `welcome-route`, `fab-menu`, `concert-highway`, `my-artists-route`, `settings-list`, `order-route`, `event-detail-sheet`); verify no entry for `cube/block-max-lines` remains for a file and that its stories' pixels are unchanged. Add a named story for any new component with a visual state, as `AGENTS.md` requires.
- [x] 8.2 Do the same for the 8 organizer stylesheets (`top-app-bar`, `concert-editor-route`, `concert-route`, `venue-field`, `console-field`, `sales-tab`, `organizer-shell`, `console-button`); verify as in 8.1, and check whether the organizer guide (`organizer/guide/guide.html`) quotes anything that moved, running `test/organizer/guide.spec.ts`.
- [x] 8.3 For any block left over 100 lines, write the reason in a described disable and list it in design.md; verify `stylelint-suppressions.json` has no `cube/block-max-lines` entries.

## 10. Defects found by the style audit (visible)

Order of the remaining groups: 10 → 11 → 12 → 6 → 7 → 8 → 9 (design "Style audit after group 5").

- [x] 10.1 Remove the global `:where(svg)` fill and stroke and the five overrides that undo it, so inline SVGs draw as written; replace the two hand-drawn SVGs (inline-error, user-home-selector back) with `<svg-icon>`. Verify the inline-error story shows the outlined info icon and the back control its chevron.
- [x] 10.2 In the organizer shell, set the property the snack bar reads (`--bottom-banner-height`) while the extended FAB shows, and remove `.main { outline: none }`. Verify with Playwright that a snack on the concerts screen sits above the FAB, and that the page area shows the focus ring when focused by keyboard.
- [x] 10.3 Delete the block-level `background: transparent`, `border: none` and `cursor: pointer` that repeat or undo the global button rules, so buttons keep the hover and focus layer and the high-contrast border. Verified by a node test that no fan block sets those declarations on a class a `<button>` carries (which also covers the high-contrast border, a global rule the block no longer overrides), and by the notification bell's Hovered story with a real pointer.

## 11. One foundation for both apps (no visible change)

- [x] 11.1 Keep the before/after layout record from group 5 as an opt-in e2e fixture (`LAYOUT_DIR`), with the comparison script, and document how to run it.
- [x] 11.2 Move the reset (lists, fieldsets, buttons, links, headings), the compositions (`flow`, `stack`, `cluster`, `center`, `wrapper`, a full-bleed composition) and `visually-hidden` into `shared/styles/`, used by `src/styles/main.css` and `organizer/styles/shared.css` alike (a `composition` layer in the console's shadow roots), settling the variable names and defaults the two apps differ on. Replace the four organizer full-bleed copies and their eight described disables with the composition.
- [x] 11.3 Delete the declarations that repeat a lower layer (`text-wrap`, `background: surface` on route roots, `color: on-surface`, `tabular-nums`, `cursor`, `border: none`, `accent-color`, svg-icon host defaults) and replace hand-made flex stacks, clusters and centring with the compositions.
- [x] 11.4 Delete dead CSS: unused utilities and keyframes, the consent route's copy of the settings switch, `.event-card-responsive`, rules and classes no template uses, stale comments; check `toast` and `auth-status` for users and delete them if none. (Both were unused. The `toast` spec is removed with its component; the auth-status unit test's i18n scenario "Sign up in English" stays covered by the Settings route test.)
- [x] 11.5 Replace values that should be tokens: local renames of tokens, `50%` radii, raw durations (one reduced-motion rule: the 0 ms tokens), `--md-target-size` and `--md-elevation-*` by the shared `--md-sys-*` tokens, repeated literals (48, 56 and 64 px, the 36rem reading width, the FAB clearance) by named tokens.
- [x] 11.6 Verify the group with the layout record from 11.1 across the functional and onboarding projects: no element box changes except where a task above names one.

## 12. Shared blocks at the Material 3 values (visible)

One PR per block family. Each new block gets a story per visual state; each PR lists every visible change with before and after images.

- [x] 12.1 Text field: one shared field block (label, input, error) for the five fan route copies, the two date fields and the global field rule; the organizer's `venue-field` reuses `console-field.css`.
- [x] 12.2 Chip: one shared chip block at the Material 3 filter-chip values (32 px, `corner-small`, selected = `secondary-container` with a leading checkmark) for the preset, artist, journey, genre and reset chips, the page-help demo and the home selector options; the bottom-sheet and bottom-nav-bar deltas replace "pill-shaped" and the brand tint with those values.
- [x] 12.3 Card and summary: one card block (`surface-container`, `outline-variant`, `corner-medium`, the Material 3 card values) for the fan panels, settings and passkeys cards and the organizer centred cards; one summary-list block for the order, ticket, lottery-status and confirmation `dl`s.
- [x] 12.4 Badge and text link: one badge block with `data-tone`; one text-link block (inline, and standalone with a target) with one colour role.
- [x] 12.5 Icon button and menu: shared icon-button, menu and menu-item blocks for the organizer copies (in `shared.css`, reaching shadow roots) and the fan close and FAB buttons where they match.
- [x] 12.6 State: hover, focus and press drawn by one state-layer mechanism in both apps, with no press scale (Material 3 has none), replacing the global button state rules and the per-block copies.
- [x] 12.7 Messages: one empty and error state (`state-placeholder`, with inline-error and the organizer message built on it); merge the two bottom banners into one block; add `.button[data-size="compact"]` for the four compact overrides; one stylesheet for the organizer lottery and ticket sale editors.

## 9. Close out

- [x] 9.1 Annotate or add tests for every scenario `python3 scripts/check-scenario-coverage.py adopt-m3-cube-ui-foundation` still reports, mainly `bottom-sheet` and `live-highway`; verify it exits 0.
- [x] 9.2 Delete `stylelint-suppressions.json` and any token still aliased for migration; verify `npm run lint:css` passes with no suppressions file and `grep` finds no `--step-`, `--leading-`, `--font-`, `--radius-`, `--shadow-` or `--md-type-` in `src/`, `shared/` and `organizer/`.
- [x] 9.3 Verify in production after the last release: open `/dashboard`, `/discovery`, `/my-artists`, `/tickets`, `/settings` and the organizer concerts screen in Playwright with the Pixel 7 and iPhone profiles, check no horizontal scroll and no clipped text, and read the rollout status; note what was checked by emulation rather than on a physical device.
