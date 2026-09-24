<!-- spec: frontend-testing | target: components/infrastructure/fan/web/global/bottom-nav-bar | flags: CLASSNAME | new_name: App shell hides navigation on fullscreen routes -->

### Requirement: App shell hides navigation on fullscreen routes
The app shell's navigation-visibility state SHALL be `false` for fullscreen routes and `true` for other routes.

#### Scenario: Fullscreen route
- **WHEN** the active route path is `welcome`, `onboarding/discover`, or `auth/callback`
- **THEN** the navigation SHALL be hidden

#### Scenario: Non-fullscreen route
- **WHEN** the active route path is `dashboard` or `about`
- **THEN** the navigation SHALL be shown
