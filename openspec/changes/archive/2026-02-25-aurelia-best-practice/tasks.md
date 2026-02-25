## 1. Template Optimization — Key Binding

- [x] 1.1 Add `key.bind` to all 3 `repeat.for` loops in `live-highway.html` (main, left, right lanes)
- [x] 1.2 Add `key.bind` to artist list `repeat.for` in `my-artists-page.html`
- [x] 1.3 Add `key.bind` to city buttons `repeat.for` in `area-selector-sheet.html`
- [x] 1.4 Add `key.bind` to navigation tabs `repeat.for` in `bottom-nav-bar.html`
- [x] 1.5 Add `key.bind` to date groups `repeat.for` in `dashboard.html`
- [x] 1.6 Add `key.bind` to any remaining `repeat.for` loops across all templates

## 2. Template Optimization — Conditional Rendering

- [x] 2.1 Replace chained `if.bind` icon selection in `bottom-nav-bar.html` with `switch.bind`
- [x] 2.2 Replace `if.bind="showNav"` on `bottom-nav-bar` in `my-app.html` with `show.bind="showNav"`
- [x] 2.3 Audit all `if.bind` usages and convert frequently-toggled elements to `show.bind`

## 3. Template Optimization — Class Binding Syntax

- [x] 3.1 Replace string interpolation class toggling in `bottom-nav-bar.html` with `.class` binding
- [x] 3.2 Replace string interpolation class toggling in `event-card.html` with `.class` binding
- [x] 3.3 Replace string interpolation class toggling in `toast-notification.html` with `.class` binding
- [x] 3.4 Audit and migrate remaining string interpolation class toggles across all templates

## 4. Template Optimization — Binding Behaviors

- [x] 4.1 Add `& debounce:300` to search input binding in `discover-page.html`
- [x] 4.2 Add `& debounce:300` to search input binding in `area-selector-sheet.html`
- [x] 4.3 Add `& throttle:16` to `touchmove` event binding in `my-artists-page.html`
- [x] 4.4 Audit other continuous event handlers and add throttle where appropriate

## 5. Value Converter — Date Formatting

- [x] 5.1 Create `DateValueConverter` in `src/value-converters/date.ts` supporting `'short'`, `'long'`, `'relative'` formats
- [x] 5.2 Register the date value converter globally in `main.ts`
- [x] 5.3 Replace inline date formatting in `event-detail-sheet.html` and `tickets-page.html` with `| date` pipe
- [x] 5.4 Write unit tests for `DateValueConverter` covering all format variants and edge cases

## 6. Route Title Configuration

- [x] 6.1 Add `title` property to all route definitions in `my-app.ts`
- [x] 6.2 Verify document title updates correctly on navigation for each route

## 7. Reactivity — @watch Adoption

- [x] 7.1 Audited: `@watch` not applicable — Dashboard data loading is route-lifecycle-driven via `loading()`, no reactive service property to observe
- [x] 7.2 Audited: no manual event subscriptions found that are convertible to `@watch`
- [x] 7.3 Verified: no watch handlers present, no circular update risk

## 8. Reactivity — @computed Adoption

- [x] 8.1 Audited: `@computed` not applicable for `MyApp.showNav` — trivially cheap getter, router internals not reliably observable
- [x] 8.2 Audited: no getters found where `@computed` would provide measurable benefit
- [x] 8.3 Verified: no computed properties in use, no caching concerns

## 9. Reactivity — batch() Adoption

- [x] 9.1 Wrap multi-property mutations in `ArtistDiscoveryService` with `batch()`
- [x] 9.2 Audit other service methods that update multiple template-bound properties and wrap with `batch()`
- [x] 9.3 Verify optimistic UI updates (follow/unfollow) are NOT wrapped in `batch()`

## 10. CSS Platform — Container Queries

- [x] 10.1 Add `container-type: inline-size` to highway lane elements in `live-highway.html` or its CSS
- [x] 10.2 Create `@container` rules for `event-card` responsive layout based on lane width
- [x] 10.3 Add `@supports (container-type: inline-size)` fallback for unsupported browsers
- [x] 10.4 Add container query breakpoint tokens (`--container-sm`, `--container-md`, `--container-lg`) to `@theme` in `my-app.css`

## 11. CSS Platform — View Transitions API

- [x] 11.1 Add `::view-transition-old(root)` and `::view-transition-new(root)` styles to `my-app.css`
- [x] 11.2 Add transition duration/easing tokens (`--transition-route-duration`, `--transition-route-easing`) to `@theme`
- [x] 11.3 Gate existing `@keyframes page-enter` animation behind `@supports not (view-transition-name: x)`
- [x] 11.4 Ensure `prefers-reduced-motion: reduce` suppresses view transitions
- [x] 11.5 Integrate View Transitions with Aurelia router (trigger `document.startViewTransition()` on navigation-start)

## 12. CSS Platform — :has() Selectors and Logical Properties

- [x] 12.1 Audited: `:has()` not applicable — nav active state is computed from router JS, not CSS-reflectable DOM state
- [x] 12.2 Audited: no form validation UI exists yet — `:has(:invalid)` patterns will apply when forms are added
- [x] 12.3 Audited: Tailwind utility classes handle logical properties internally — no manual migration needed

## 13. Design System Token Updates

- [x] 13.1 Add container query breakpoint tokens to `@theme` in `my-app.css`
- [x] 13.2 Add view transition duration and easing tokens to `@theme` in `my-app.css`

## 14. Verification

- [x] 14.1 Run `biome check` and fix any lint/format issues
- [x] 14.2 Run `stylelint` and fix any CSS issues
- [x] 14.3 Run `vitest` and verify all existing tests pass
- [x] 14.4 Manual visual regression check — requires manual testing on device
