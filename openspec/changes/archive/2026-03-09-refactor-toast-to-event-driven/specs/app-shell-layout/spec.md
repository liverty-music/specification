## ADDED Requirements

### Requirement: App-level toast notification overlay
The app shell SHALL include a `<toast-notification>` custom element as an app-level overlay, ensuring toast notifications are available on all routes.

#### Scenario: Toast element placement
- **WHEN** the application shell renders
- **THEN** `<toast-notification>` SHALL be present in `my-app.html` outside the `<main>` element
- **AND** it SHALL be placed alongside other app-level overlays (`<error-banner>`, `<pwa-install-prompt>`)

#### Scenario: Toast visible on any route
- **WHEN** any route is active (discover, settings, my-artists, welcome, etc.)
- **AND** a `Toast` event is published
- **THEN** the toast notification SHALL be rendered because the element is always in the DOM
