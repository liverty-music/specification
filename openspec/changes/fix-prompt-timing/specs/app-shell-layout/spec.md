# App Shell Layout -- Delta (fix-prompt-timing)

## MODIFIED Requirements

### Requirement: Notification Prompt Placement (MODIFIED)

The notification prompt SHALL be rendered at the app shell level (`my-app.html`) rather than within the dashboard route template. This ensures the prompt is available on any post-onboarding route, not only the dashboard.

#### Scenario: Notification prompt rendered in app shell when eligible

- **WHEN** the user is authenticated (`auth.isAuthenticated === true`)
- **AND** onboarding is completed (`onboarding.isCompleted === true`)
- **AND** the navigation bar is visible (`showNav === true`)
- **THEN** the system SHALL render the `<notification-prompt>` component in the app shell
- **AND** the prompt SHALL appear above the main content area, below any app-level banners

#### Scenario: Notification prompt hidden during onboarding routes

- **WHEN** the user is on a fullscreen route (Landing Page, Loading Sequence, Auth Callback)
- **OR** the user is not authenticated
- **OR** onboarding is not completed
- **THEN** the system SHALL NOT render the `<notification-prompt>` component

#### Scenario: Notification prompt removed from dashboard route

- **WHEN** the dashboard route template is rendered
- **THEN** the template SHALL NOT contain a `<notification-prompt>` element
- **AND** the notification prompt import SHALL be removed from the dashboard template
