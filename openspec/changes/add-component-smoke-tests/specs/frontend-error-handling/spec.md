# Frontend Error Handling — Delta

## MODIFIED Requirements

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
