# Error Banner

## Purpose

Catches unhandled application and routing errors, sanitizes and stores them, and surfaces a global error banner so the user is informed without the page crashing, ignoring errors from fetches cancelled by navigation.

## Requirements

### Requirement: Global Error Handler Registration
The system SHALL register global error handlers during Aurelia 2 application startup using `AppTask.creating()` to catch all unhandled errors and promise rejections.

#### Scenario: Unhandled synchronous error is caught
- **WHEN** an unhandled error occurs anywhere in the application
- **THEN** the system SHALL intercept the error via `window.onerror`
- **AND** the system SHALL generate a unique Error ID in the format `ERR-{8-char-hex}`
- **AND** the system SHALL pass the error to the `ErrorBoundaryService`
- **AND** the system SHALL prevent the default browser error handling

#### Scenario: Unhandled promise rejection is caught
- **WHEN** a promise rejects without a `.catch()` handler
- **THEN** the system SHALL intercept the rejection via `unhandledrejection` event listener
- **AND** the system SHALL generate a unique Error ID
- **AND** the system SHALL pass the rejection reason to the `ErrorBoundaryService`
- **AND** the system SHALL prevent the default browser error handling

---

### Requirement: Captured errors are stored and exposed for display
The system SHALL provide an `ErrorBoundaryService` as a DI singleton that captures, stores, and exposes errors for reactive UI display.

#### Scenario: Error is captured with context
- **WHEN** `ErrorBoundaryService.captureError(error, context?)` is called
- **THEN** the service SHALL create an `AppError` object containing the error message, stack trace, timestamp, Error ID, source context, and current route URL
- **AND** the service SHALL set `currentError` observable to the new `AppError`
- **AND** the service SHALL append the error to the circular error history buffer (max 20 entries)
- **AND** the service SHALL log the error via `ILogger`

#### Scenario: User dismisses error
- **WHEN** the user clicks the "Dismiss" button on the error banner
- **THEN** the service SHALL set `currentError` to `null`
- **AND** the error SHALL remain in the error history buffer

#### Scenario: Breadcrumb tracking
- **WHEN** the user performs a click, navigation, or form submission
- **THEN** the service SHALL record a breadcrumb entry containing the event type, element identifier, timestamp, and current route
- **AND** the service SHALL maintain a circular buffer of the last 30 breadcrumbs
- **AND** breadcrumbs SHALL be included in error reports when an error occurs

---

### Requirement: Error Banner UI in Root Component
The system SHALL display an error banner in the root component (`my-app`) when `ErrorBoundaryService.currentError` is set.

#### Scenario: Error banner renders with error details
- **WHEN** `ErrorBoundaryService.currentError` is not null
- **THEN** the root component SHALL display an error banner overlaying the current page content
- **AND** the banner SHALL display a user-friendly error message
- **AND** the banner SHALL display the Error ID prominently
- **AND** the banner SHALL provide a "Copy Error Details" button
- **AND** the banner SHALL provide a "Report to GitHub" button
- **AND** the banner SHALL provide a "Dismiss" button
- **AND** the banner SHALL provide a "Reload Page" button

#### Scenario: Error banner buttons are interactive
- **WHEN** the error banner dialog is displayed via `showModal()`
- **THEN** all buttons within the dialog SHALL respond to click and tap events
- **AND** the dialog element SHALL override the inherited `pointer-events: none` from the parent `<error-banner>` custom element with `pointer-events: auto`
- **AND** the `::backdrop` pseudo-element SHALL NOT block pointer events from reaching the dialog content

#### Scenario: Copy Error Details generates Markdown report
- **WHEN** the user clicks "Copy Error Details"
- **THEN** the system SHALL copy a Markdown-formatted error report to the clipboard
- **AND** the report SHALL include: Error ID, timestamp, current URL, error message, stack trace, browser user agent, recent breadcrumbs (last 10), and recent network errors
- **AND** the report SHALL NOT include authentication tokens or sensitive headers
- **AND** the system SHALL display a brief confirmation toast "Error details copied"

#### Scenario: Report to GitHub opens pre-filled issue
- **WHEN** the user clicks "Report to GitHub"
- **THEN** the system SHALL open a new browser tab to `https://github.com/liverty-music/frontend/issues/new`
- **AND** the URL SHALL include query parameters for `title` (containing Error ID) and `body` (containing the Markdown error report)
- **AND** the URL SHALL include a `labels` parameter with value `bug`
- **AND** the "Report to GitHub" button SHALL be rate-limited to one click per 60 seconds

---

### Requirement: Router Error Handling
The system SHALL handle navigation errors gracefully using Aurelia 2 router configuration and events.

#### Scenario: Navigation error restores previous route
- **WHEN** a navigation fails due to an error in `canLoad()` or `loading()` hooks
- **AND** the environment is production
- **THEN** the router SHALL restore the previous valid route tree (`restorePreviousRouteTreeOnError: true`)
- **AND** the error SHALL be captured by `ErrorBoundaryService`
- **AND** the user SHALL see the error banner while remaining on the last valid page

#### Scenario: Navigation error in development shows error state
- **WHEN** a navigation fails due to an error in lifecycle hooks
- **AND** the environment is development
- **THEN** the router SHALL NOT restore the previous route (`restorePreviousRouteTreeOnError: false`)
- **AND** the error SHALL be displayed with full stack trace details

#### Scenario: 404 fallback route
- **WHEN** a user navigates to a URL that does not match any defined route
- **THEN** the router SHALL display a "Page Not Found" component
- **AND** the component SHALL provide a link to navigate to the dashboard

#### Scenario: Navigation error event subscription
- **WHEN** a `au:router:navigation-error` event is fired by the router
- **THEN** the root component SHALL pass the error to `ErrorBoundaryService.captureError()` with context `"router:navigation-error"`

---

### Requirement: Error boundary service captures and sanitizes errors
The `ErrorBoundaryService` SHALL capture application errors, maintain a capped history, track breadcrumbs, and generate sanitized error reports.

#### Scenario: Capture error adds to history
- **WHEN** `captureError` is called with an error
- **THEN** the error SHALL be added to the history and set as `currentError`

#### Scenario: History is capped
- **WHEN** the error history exceeds the maximum size
- **THEN** the oldest entry SHALL be removed

#### Scenario: Sanitize redacts sensitive tokens
- **WHEN** `generateReport` is called for an error containing Bearer tokens or JWT strings
- **THEN** the report SHALL redact those tokens

#### Scenario: GitHub issue URL is constructed correctly
- **WHEN** `buildGitHubIssueUrl` is called
- **THEN** it SHALL return a valid GitHub URL with pre-filled title and body

#### Scenario: Dismiss clears current error
- **WHEN** `dismiss` is called
- **THEN** `currentError` SHALL be set to `null`

### Requirement: Navigating away from a route suppresses its cancelled fetch as an error
Because the fetch outlives `loading()`, a menu-tab route SHALL abort its in-flight request when the route is deactivated, and an `AbortError` SHALL be treated as a non-error.

#### Scenario: Leaving the tab aborts the request
- **WHEN** the user navigates away from a menu-tab route before its fetch resolves
- **THEN** the route's deactivation hook SHALL abort the request's `AbortController`
- **AND** the resulting `AbortError` SHALL NOT be logged as an error or shown to the user
