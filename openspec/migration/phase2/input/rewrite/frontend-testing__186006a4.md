<!-- spec: frontend-testing | target: components/infrastructure/fan/web/global/bottom-nav-bar | flags: CLASSNAME | new_name: App shell hides navigation on fullscreen routes -->

### Requirement: MyApp showNav hides navigation on fullscreen routes
The `MyApp.showNav` getter SHALL return `false` for fullscreen routes and `true` for other routes.

#### Scenario: Fullscreen route
- **WHEN** the active route path is `welcome`, `onboarding/discover`, or `auth/callback`
- **THEN** `showNav` SHALL return `false`

#### Scenario: Non-fullscreen route
- **WHEN** the active route path is `dashboard` or `about`
- **THEN** `showNav` SHALL return `true`
