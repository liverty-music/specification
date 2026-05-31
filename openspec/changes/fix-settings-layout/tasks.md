# Tasks

## 1. Layout / scroll fix

- [x] 1.1 Refactor `settings-route.css` `main` to the house scroll pattern:
      `overflow: hidden; min-block-size: 0;` and move scrolling to an inner
      `.settings-scroll` container (`flex: 1; overflow-y: auto;`) holding the
      `<section>` list, preserving the gutters.
- [x] 1.2 Update `settings-route.html` so the section list lives inside the new
      inner scroll container; keep `page-header` pinned outside it.
- [ ] 1.3 Verify against siblings in-browser: first row (My Home Area) visible
      on load, header not overlapped, list scrolls within the content area,
      bottom nav unaffected. (Pending: run the app / refresh visual baseline.)

## 2. CUBE CSS alignment

- [x] 2.1 Use the `[ stack ]` composition for the section list and language list
      rhythm instead of hand-rolled flex+gap; keep only skin in `@layer block`
      and do NOT re-declare composition `display/flex/gap` (block wins over
      composition in the cascade order).
- [x] 2.2 Remove the single-block bracket wrapper `class="[ settings-divider ]"`;
      apply bracket grouping only for `[ block ] [ composition ] [ utilities ]`.
- [x] 2.3 `make lint` (biome + stylelint + cube-css lint plugin + typecheck)
      clean — 0 errors. (Pre-existing `.settings-volume-slider` order warning
      left untouched.)

## 3. Tests

- [x] 3.1 `make lint` + unit tests (`test/routes/settings-route.spec.ts`, 28)
      green after the change (ViewModel untouched; CSS/HTML only).
- [ ] 3.2 Add `data-testid` per `layout-assertions` and a visual/layout E2E
      assertion that the first preferences row is visible (not clipped by the
      header); refresh the `settings.auth.visual.spec.ts` screenshot baseline.
      (Pending: requires running Playwright / a dev or mocked build.)

## 4. Ship

- [ ] 4.1 Open frontend PR; CI green; address review; merge to `main`.
- [ ] 4.2 Cut frontend GitHub Release → prod AR retag.
- [ ] 4.3 cloud-provisioning prod image pin-bump PR → ArgoCD auto-sync;
      confirm the fix is live in prod.
- [ ] 4.4 Archive this OpenSpec change once all tasks are complete.
