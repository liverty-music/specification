<!-- spec: pwa-update-lifecycle | target: components/infrastructure/fan/web/service-worker | flags: CLASSNAME | new_name: The SPA registers its Service Worker on boot -->

### Requirement: The app registers its service worker via the platform's PWA registration mechanism

The app SHALL register its service worker through the PWA registration mechanism provided by the build tooling, configured to prompt the user before applying updates (`registerType: 'prompt'`), rather than using a direct low-level registration call. The registration SHALL be invoked at application startup and SHALL be skipped outside production environments.

#### Scenario: Service worker is registered via the PWA registration mechanism in production

- **WHEN** the app loads in a production environment
- **THEN** the service worker SHALL be registered through the PWA registration mechanism
- **AND** a direct low-level registration call SHALL NOT exist in the entry point

#### Scenario: Service worker registration is skipped in dev mode

- **WHEN** the app loads under the development server
- **THEN** the service worker registration SHALL NOT be invoked
- **AND** no service worker SHALL be registered
