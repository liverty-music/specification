## 1. Dependencies and Configuration

- [x] 1.1 Install `stylelint-order` and `stylelint-config-clean-order` npm packages
- [x] 1.2 Update `.stylelintrc.json` with full rule configuration: extends (standard + clean-order), function-disallowed-list, color-no-hex, property-disallowed-list (all physical properties + z-index + float + clear), media-feature-name-disallowed-list (width, min-width, max-width), declaration-no-important, selector-max-id, selector-max-specificity, selector-max-compound-selectors, number-max-precision, at-rule-no-unknown ignoreAtRules, function-no-unknown ignoreFunctions
- [x] 1.3 Add `.stylelintrc.json` to `paths-filter` in `ci.yaml` so stylelint config-only changes trigger the lint job
- [x] 1.4 Verify `npm run lint:css` executes successfully with the new configuration (expect violations in existing files)

## 2. Color Migration (rgb/rgba/hex to oklch)

- [x] 2.1 Migrate all `rgb()`/`rgba()` color values in `discover-page.css` to `oklch()`
- [x] 2.2 Migrate all `rgb()`/`rgba()` color values in `loading-sequence.css` to `oklch()`
- [x] 2.3 Migrate any remaining `rgb()`/`rgba()`/hex values in other CSS files (`dna-orb-canvas.css`, `coach-mark.css`, `my-app.css`, etc.) to `oklch()`
- [x] 2.4 Verify no `function-disallowed-list` or `color-no-hex` violations remain

## 3. Physical Property Migration (to Logical Properties)

- [x] 3.1 Migrate `margin-left` in `discover-page.css` to `margin-inline-start`
- [x] 3.2 Migrate `left: 50%` + `bottom: Xrem` positioning patterns in `discover-page.css` to `inset-inline-start` / `inset-block-end`
- [x] 3.3 Migrate `top: 0; left: 0` in `loading-sequence.css` to `inset: 0` (or `inset-block-start` / `inset-inline-start`)
- [x] 3.4 Migrate `margin-top` / `margin-bottom` in `loading-sequence.css` and `coach-mark.css` to `margin-block-start` / `margin-block-end`
- [x] 3.5 Migrate `padding-top` / `padding-bottom` in `discover-page.css` to `padding-block-start` / `padding-block-end`
- [x] 3.6 Verify no `property-disallowed-list` violations remain

## 4. Media Query Migration (viewport-width to container)

- [x] 4.1 Convert `@media (width <= 640px)` in `loading-sequence.css` to `@container` query (add `container-type: inline-size` to parent element)
- [x] 4.2 Verify no `media-feature-name-disallowed-list` violations remain

## 5. Property Order Autofix

- [x] 5.1 Run `npx stylelint "src/**/*.css" --fix` to auto-sort property declaration order across all files
- [x] 5.2 Review the property order changes for correctness (no semantic changes, only reordering)

## 6. Validation

- [x] 6.1 Run `npm run lint:css` and confirm zero violations
- [x] 6.2 Run `make check` and confirm full pipeline passes (Biome + Stylelint + tests)
- [x] 6.3 Visual smoke test: verify `npm start` renders key pages correctly (discover page starfield, loading sequence, coach-mark tooltip)
