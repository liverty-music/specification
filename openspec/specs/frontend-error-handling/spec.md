# Frontend Error Handling

## Purpose

Defines the global error handling infrastructure for the Aurelia 2 frontend, ensuring that unhandled errors never crash the page to a white screen. Provides structured error capture, user-facing error UI with one-click GitHub Issue reporting, declarative async error handling via `promise.bind`, and service-level error recovery patterns.

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

### Requirement: Error Boundary Service
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

### Requirement: Declarative Async Error Handling with promise.bind
The system SHALL use Aurelia 2's `promise.bind` template pattern for all async data rendering to provide declarative pending, success, and error states.

#### Scenario: Data loading with pending state
- **WHEN** a component loads async data via `promise.bind`
- **THEN** the template SHALL display a loading skeleton or spinner during the pending state

#### Scenario: Data loading succeeds
- **WHEN** the bound promise resolves successfully
- **THEN** the template SHALL render the data in the `then` block

#### Scenario: Data loading fails with error UI
- **WHEN** the bound promise rejects
- **THEN** the template SHALL display an error message in the `catch` block
- **AND** the error UI SHALL include a "Retry" button that re-invokes the data loading function
- **AND** the error UI SHALL display a brief, user-friendly description of what failed

---

### Requirement: Service Error Recovery Patterns
The system SHALL replace silent error swallowing in services with explicit error states that callers can distinguish from empty-data states.

#### Scenario: Service method returns error result instead of empty fallback
- **WHEN** a service method fails to fetch data from the backend
- **THEN** the method SHALL throw the error to the caller (not silently return an empty array or false)
- **AND** the caller SHALL handle the error via `promise.bind` catch block or explicit try/catch with user feedback

#### Scenario: Fire-and-forget operations provide user feedback on failure
- **WHEN** a fire-and-forget RPC operation (e.g., artist follow) fails
- **THEN** the system SHALL display a toast notification informing the user of the failure
- **AND** the system SHALL revert any optimistic UI updates
