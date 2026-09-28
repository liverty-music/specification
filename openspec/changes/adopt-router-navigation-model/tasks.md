## 1. Spikes (design.md S1, S2)

- [ ] 1.1 S1: in a unit test against the real router, configure one route with `path: ['dashboard', 'concerts/:id']` and `nav: true`, navigate to `concerts/abc`, and record whether its `NavigationRoute.isActive` is true. Record the result in design.md D2; if false, switch D2 to the child-route fallback before starting group 2
- [ ] 1.2 S2: in a shell-level test, confirm a custom element rendered beside `<au-viewport>` resolves `IRouteContext` whose `navigationModel.routes` lists the top-level `nav: true` routes, and that a binding to `ICurrentRoute.parameterInformation[0].config.data.titleKey` updates after navigation. Record the result in design.md D1/D3; if the context does not resolve, adopt the bindable fallback

## 2. Route configuration (bottom-nav-bar: "Active tab reflects the displayed route")

- [ ] 2.1 In `app-shell.ts`, mark the five tab routes `nav: true`, move each tab's icon and label key into `data.icon` / `data.labelKey`, give the dashboard route an explicit `id`, and merge `concerts/:id` into it per D2; verify `npm run typecheck` and the existing deep-link unit tests in `dashboard-route.spec.ts` pass unchanged
- [ ] 2.2 Rename `data.nav: false` to `data.chrome: false` and read it in `showNav` (D6); verify the shell test for hidden chrome on `welcome` and `auth/callback` passes

## 3. Bottom nav bar (bottom-nav-bar: "Active tab reflects the displayed route")

- [ ] 3.1 Render tabs from `navigationModel.routes` (link, `data-nav` from `data.icon`, label from `data.labelKey`, `data-active` from `isActive`); delete the `tabs` array, `isActive()` and the `IPageHeaderState` dependency; verify by rewriting `bottom-nav-bar.spec.ts` and `test/components/bottom-nav-bar.fixture.spec.ts` to cover the scenarios "Tab route displayed", "Concert deep-link highlights Home" and "Route outside every tab" against the real router

## 4. Page header (page-header: "Page identity follows the displayed route", "Page header is a single shell-hosted instance…")

- [ ] 4.1 Bind the shell's `<page-header>` title to the current route's `data.titleKey` via one `AppShell` getter over `ICurrentRoute` (D3); remove the `morph-title` bindable and its `view-transition-name` from `page-header` (`.ts`, `.html`, `.css`, stories); verify `test/app-shell.spec.ts` covers "Header title and active tab match the route shown", "Redirects and the fallback route are reflected" and "Routes without a title show no header"
- [ ] 4.2 Remove the `navigation-start` and `navigation-error` identity handling, `resolvePageIdentity`, `normalizePath`, `pathMatches` and `identityFromNode` from `app-shell.ts`; delete `services/page-header-state.ts`, its spec, and its registration in `main.ts`; verify `make lint` and `make test` pass and `grep -r IPageHeaderState src test` is empty

## 5. Dashboard (route/dashboard: "Dashboard Mode Toggle", "Natural Japanese Copy for All Nearby")

- [ ] 5.1 Remove `modeTitleKey` and both `setTitle` calls from `dashboard-route.ts`, keeping the mode switch's content View Transition; remove the now-unused mode-title keys from both i18n bundles; verify a dashboard unit test covers "Header title does not change with the mode" and the i18n parity check passes

## 6. End-to-end

- [ ] 6.1 Rewrite `e2e/functional/instant-page-switch.spec.ts` to assert that identity matches the displayed route: tab switch, a `/concerts/:id` deep-link highlighting Home, and a navigation blocked by a guard leaving the previous title and tab in place ("A failed navigation leaves identity unchanged"); verify it passes in the functional Playwright project
- [ ] 6.2 Run the full Playwright suite (functional and onboarding projects) and verify no selector relying on `data-nav` or the header title regressed
