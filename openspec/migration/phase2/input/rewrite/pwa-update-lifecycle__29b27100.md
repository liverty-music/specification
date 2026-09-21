<!-- spec: pwa-update-lifecycle | target: components/infrastructure/fan/web/service-worker | flags: CLASSNAME | new_name: The SPA registers its Service Worker on boot -->

### Requirement: The SPA SHALL register its Service Worker via `virtual:pwa-register`

The SPA SHALL use the `registerSW` function from `virtual:pwa-register` (provided by `vite-plugin-pwa`) in place of the bare `navigator.serviceWorker.register()` call. The `registerType` configuration SHALL be set to `'prompt'`. The registration SHALL be invoked in the SPA bootstrap entry point and SHALL be guarded against non-production environments (`import.meta.env.DEV`).

#### Scenario: SW is registered via virtual module in production

- **WHEN** the SPA loads in a browser where `import.meta.env.DEV` is `false`
- **THEN** `registerSW` from `virtual:pwa-register` SHALL be invoked
- **AND** the bare `navigator.serviceWorker.register('/sw.js')` call SHALL NOT exist in the entry point

#### Scenario: SW registration is skipped in dev mode

- **WHEN** the SPA loads under the Vite dev server (`import.meta.env.DEV === true`)
- **THEN** `registerSW` SHALL NOT be called
- **AND** no service worker SHALL be registered
