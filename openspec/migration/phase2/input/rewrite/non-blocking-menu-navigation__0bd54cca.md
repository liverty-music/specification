<!-- spec: non-blocking-menu-navigation | target: components/infrastructure/fan/web/global/error-banner | flags: CLASSNAME | new_name: Navigating away from a route suppresses its cancelled fetch as an error -->

### Requirement: Navigating away cancels the in-flight fetch
Because the fetch outlives `loading()`, a menu-tab route SHALL abort its in-flight request when the route is deactivated, and an `AbortError` SHALL be treated as a non-error.

#### Scenario: Leaving the tab aborts the request
- **WHEN** the user navigates away from a menu-tab route before its fetch resolves
- **THEN** the route's deactivation hook SHALL abort the request's `AbortController`
- **AND** the resulting `AbortError` SHALL NOT be logged as an error or shown to the user
