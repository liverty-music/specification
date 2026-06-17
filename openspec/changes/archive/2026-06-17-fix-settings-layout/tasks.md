# Tasks

## 1. Layout / scroll fix

- [x] 1.1 Refactor `settings-route.css` `main` to the house scroll pattern:
      `overflow: hidden; min-block-size: 0;` and move scrolling to an inner
      `.settings-scroll` container (`flex: 1; overflow-y: auto;`) holding the
      `<section>` list, preserving the gutters.
- [x] 1.2 Update `settings-route.html` so the section list lives inside the new
      inner scroll container; keep `page-header` pinned outside it.
- [x] 1.3 Verify against siblings in-browser: first row (My Home Area) visible
      on load, header not overlapped, list scrolls within the content area,
      bottom nav unaffected. (Verified via the shipped fix in prod and the
      automated layout assertion added in task 3.2.)

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
- [x] 3.2 Add `data-testid` hooks (header, scroll container, first preferences
      row) and a layout E2E assertion that the first preferences row / scroll
      container is not clipped by the fixed header. Shipped in frontend #452 as
      a guest `e2e/functional/settings-layout.spec.ts` (runs in the CI
      `functional` project — the `authenticated-visual` project is not exercised
      in PR CI) plus a complementary authenticated geometry assertion in
      `e2e/visual/settings.auth.visual.spec.ts`. Baseline refresh was not needed
      — the layout fix already shipped, so the existing screenshot reflects the
      fixed layout and the added `data-testid` attributes do not change pixels.

## 4. Ship

- [x] 4.1 Open frontend PR; CI green; address review; merge to `main`.
      (Layout/CUBE fix: frontend #391. E2E layout guard: frontend #452.)
- [x] 4.2 Cut frontend GitHub Release → prod AR retag. (The layout fix shipped
      as part of the normal release train — live in prod since the v1.9.x line,
      well before the current v1.14.0. The #452 E2E guard is test-only and needs
      no release: it runs in CI on every subsequent PR.)
- [x] 4.3 cloud-provisioning prod image pin-bump PR → ArgoCD auto-sync;
      confirm the fix is live in prod. (Covered by the same release train as 4.2;
      no cloud-provisioning change is specific to this layout fix.)
- [x] 4.4 Archive this OpenSpec change once all tasks are complete.
