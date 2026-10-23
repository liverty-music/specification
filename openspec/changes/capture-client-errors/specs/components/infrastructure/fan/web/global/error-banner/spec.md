# Spec Delta

## MODIFIED Requirements

### Requirement: Global Error Handler Registration
The system SHALL register global error handlers when the application starts, so that every unhandled error and unhandled promise rejection is captured. The handlers SHALL leave the browser's own error log in place, SHALL keep a handler registered earlier by another script working, and SHALL never throw themselves.

#### Scenario: Unhandled synchronous error is caught
- **WHEN** an unhandled error occurs anywhere in the application
- **THEN** the system SHALL intercept the error
- **AND** the system SHALL generate a unique Error ID in the format `ERR-{8-char-hex}`
- **AND** the system SHALL pass the error to the `ErrorBoundaryService` with the source "unhandled error"
- **AND** the browser SHALL still log the error to its console

#### Scenario: Unhandled promise rejection is caught
- **WHEN** a promise rejects without a `.catch()` handler
- **THEN** the system SHALL intercept the rejection
- **AND** the system SHALL generate a unique Error ID
- **AND** the system SHALL pass the rejection reason, as it was rejected, to the `ErrorBoundaryService` with the source "unhandled rejection"
- **AND** the browser SHALL still log the rejection to its console

#### Scenario: An earlier error handler keeps working
- **WHEN** another script registered its own handler for unhandled errors before the application started, and an unhandled error occurs
- **THEN** that handler SHALL still receive the error
- **AND** the system SHALL capture the error as well

#### Scenario: Error without an error object keeps its location
- **WHEN** the browser reports an unhandled error with a message, file, line and column but no error object (a script error from another origin, for example)
- **THEN** the captured error SHALL carry that message, file, line and column

#### Scenario: Error raised by a browser extension
- **WHEN** an unhandled error or rejection is raised from a browser extension's code (an address starting with `chrome-extension://`, `moz-extension://`, `safari-extension:` or `safari-web-extension:`)
- **THEN** the system SHALL NOT open the error banner
- **AND** the system SHALL NOT report the error to the team

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
- **WHEN** the user clicks the 閉じる (Close) button on the error banner
- **THEN** the service SHALL set `currentError` to `null`
- **AND** the error SHALL remain in the error history buffer

#### Scenario: Breadcrumb tracking
- **WHEN** the fan moves to another screen, a request to the backend fails, or the fan performs a key action
- **THEN** the service SHALL record a step with its type (navigation, failed request, action), a label, a timestamp and the current route
- **AND** a navigation step SHALL be labelled with the screen name, a failed-request step with the method name and the error code, and an action step with the action's name
- **AND** a step SHALL NOT contain text the fan typed, an id, or a query string
- **AND** the service SHALL keep the last 30 steps
- **AND** the steps SHALL be included in the error report sent to the team

#### Scenario: Same error does not reopen a closed banner
- **WHEN** the fan closed the banner for an error, and an error with the same message and source is captured again within 60 seconds
- **THEN** the error SHALL be added to the history and reported to the team
- **AND** the banner SHALL stay closed

#### Scenario: Same error does not replace the open banner
- **WHEN** the banner is open for an error and an error with the same message and source is captured again
- **THEN** the banner SHALL keep showing the first error's Error ID

---

### Requirement: The banner's text comes from the app's catalog

The error banner SHALL show a title, a message and its button labels from the app's own catalog in the fan's language, with the Error ID labelled お問い合わせ番号 (inquiry number), and SHALL NOT show the captured error's message. The title SHALL be うまく動きませんでした (Something went wrong). The message SHALL depend on whether the error was reported to the team:

| case | Japanese message | English message |
|---|---|---|
| sent | 起きたことはチームに届いています。ページを読み込み直してみてください。よければ、何をしていたかメールで教えてください。ひとことだけで大丈夫です。 | Our team has received the details. Try reloading the page. If you like, email us what you were doing. One line is enough. |
| not sent | 起きたことはチームに届いていません。ページを読み込み直してみてください。何をしていたかメールで教えてください。ひとことだけで大丈夫です。 | Our team hasn't received the details. Try reloading the page. Please email us what you were doing. One line is enough. |

The error's message stays in the browser console log and, when the error was not reported, in the report email.

#### Scenario: Unhandled error shows fixed copy

- **WHEN** an unhandled promise rejection with the message `Cannot read properties of undefined (reading 'id')` opens the error banner for a fan using Japanese, with analytics on
- **THEN** the banner shows うまく動きませんでした, the sent message and お問い合わせ番号 with the Error ID, and `Cannot read properties` appears nowhere in the banner

#### Scenario: English labels

- **WHEN** the error banner opens for a fan using English
- **THEN** the title, the message and the button labels are in English

#### Scenario: Not-sent copy when analytics is off

- **WHEN** the error banner opens for a fan using Japanese who turned analytics off in Settings
- **THEN** the banner shows the not-sent message 起きたことはチームに届いていません。…

## ADDED Requirements

### Requirement: Captured errors are reported to the team

Every error the `ErrorBoundaryService` captures SHALL be sent as an error report to the error-reporting service of the app's usage analytics, unless the fan turned analytics off in Settings or the error came from a browser extension. A report SHALL carry:
- the error's type, message and stack, resolved to the app's source;
- the Error ID and the source of the error (unhandled error, unhandled rejection, navigation error, or the name of the place that captured it);
- the steps recorded before the error;
- the current address, under the query rule of `components/infrastructure/fan/web/global/analytics`;
- the app release;
- when the error came from a request to the backend, that request's trace ID.

An error that wraps a cause SHALL be reported with its cause, and a rejection value that is not an error object SHALL be reported as it was. A report SHALL NOT contain authentication tokens, JWTs or OIDC `code`/`state` values; they are redacted before the report leaves the device. Failing to send a report SHALL NOT throw and SHALL NOT stop the banner from opening.

#### Scenario: Error is reported with its Error ID and steps
- **WHEN** a fan with analytics on opens the dashboard, then the event detail, and an unhandled error occurs
- **THEN** one error report is sent with the banner's Error ID, the source "unhandled error" and the navigation steps for the dashboard and the event detail

#### Scenario: Failed request carries its trace ID
- **WHEN** a request to the backend fails with Internal and the error reaches the `ErrorBoundaryService`
- **THEN** the error report carries the trace ID the request sent to the backend
- **AND** its steps include a failed-request step with the method name and the code Internal

#### Scenario: Analytics off sends no report
- **WHEN** a fan who turned analytics off in Settings hits an unhandled error
- **THEN** no error report leaves the device
- **AND** the banner opens with the not-sent message

#### Scenario: Error with a cause
- **WHEN** an error whose cause is another error is captured
- **THEN** the error report contains both errors

#### Scenario: Rejection with a plain value
- **WHEN** a promise is rejected with the object `{ code: 3 }` and nothing handles it
- **THEN** the error report records that value as the rejection, not the text `[object Object]`

#### Scenario: Tokens are redacted from the report
- **WHEN** an error whose message contains `Bearer abc.def` or a JWT is reported
- **THEN** the error report contains `Bearer [REDACTED]` or `[JWT_REDACTED]` in its place

#### Scenario: Reporting failure does not break the banner
- **WHEN** sending the error report throws
- **THEN** the banner still opens, with the not-sent message

#### Scenario: Report accepted after the banner opened
- **WHEN** an error is captured before error reporting has finished loading, and the report is accepted once it loads
- **THEN** the banner first shows the not-sent message and then switches to the sent message

---

### Requirement: Error banner offers reload, close and an email report
The system SHALL display an error banner in the root component (`my-app`) when `ErrorBoundaryService.currentError` is set. The banner SHALL offer ページを読み込み直す (Reload page) as its primary button, 閉じる (Close), and メールで状況を伝える (Tell us what happened by email). When the error was reported to the team, メールで状況を伝える SHALL be a text link; when it was not, it SHALL be a button. The banner SHALL NOT link to GitHub or any other public tracker.

#### Scenario: Error banner renders with error details
- **WHEN** `ErrorBoundaryService.currentError` is not null
- **THEN** the root component SHALL display an error banner overlaying the current page content
- **AND** the banner SHALL display a user-friendly error message
- **AND** the banner SHALL display the Error ID prominently, labelled お問い合わせ番号
- **AND** the banner SHALL provide a ページを読み込み直す button, a 閉じる button and メールで状況を伝える

#### Scenario: Error banner buttons are interactive
- **WHEN** the error banner dialog is displayed via `showModal()`
- **THEN** all buttons and links within the dialog SHALL respond to click and tap events
- **AND** the dialog element SHALL override the inherited `pointer-events: none` from the parent `<error-banner>` custom element with `pointer-events: auto`
- **AND** the `::backdrop` pseudo-element SHALL NOT block pointer events from reaching the dialog content

#### Scenario: Email report is a link when the report was sent
- **WHEN** the banner opens for an error that was reported to the team
- **THEN** メールで状況を伝える is shown as a text link, not a button

#### Scenario: Email report is a button when the report was not sent
- **WHEN** the banner opens for an error that was not reported to the team
- **THEN** メールで状況を伝える is shown as a button next to 閉じる

#### Scenario: Email report opens a pre-filled message
- **WHEN** the fan taps メールで状況を伝える
- **THEN** the fan's mail app opens a message to `pannpers@pannpers.dev`, the contact address the terms of service publish, in the same tab
- **AND** the subject SHALL be アプリがうまく動きませんでした（お問い合わせ番号：<Error ID>）
- **AND** the body SHALL start with the hint そのとき何をしていたか、ひとことお願いします。 and the example 例：ライブの詳細を開こうとした, followed by blank lines for the fan's text
- **AND** below a `---` line and ここから下は、そのまま送ってください。, the body SHALL list お問い合わせ番号, 日時 (the time the error was captured, in the fan's time zone) and 画面 (the route path, without its query string)
- **AND** a second tap within 60 seconds SHALL NOT open another message and SHALL show もう一度メールを開くには、少し待ってください。

#### Scenario: Not-sent email carries the investigation details
- **WHEN** the fan taps メールで状況を伝える on the banner of an error that was not reported to the team
- **THEN** the body SHALL also contain a block titled 調査用の情報 with the error message, redacted and cut to 200 characters, and the trace ID of the failing request when there is one

#### Scenario: Sent email carries no technical details
- **WHEN** the fan taps メールで状況を伝える on the banner of an error that was reported to the team
- **THEN** the body SHALL NOT contain the error message, the stack or the trace ID

---

### Requirement: Error boundary service captures errors and builds the report email
The `ErrorBoundaryService` SHALL capture application errors, maintain a capped history, track steps, and build the report email.

#### Scenario: Capture error adds to history
- **WHEN** `captureError` is called with an error
- **THEN** the error SHALL be added to the history and set as `currentError`

#### Scenario: History is capped
- **WHEN** the error history exceeds the maximum size
- **THEN** the oldest entry SHALL be removed

#### Scenario: Sanitize redacts sensitive tokens
- **WHEN** the report email is built for an unreported error whose message contains a Bearer token or a JWT string
- **THEN** the email SHALL redact those tokens

#### Scenario: Report email link is constructed correctly
- **WHEN** the report email link is built for an unreported error whose message is 10,000 characters long
- **THEN** it SHALL be a `mailto:` link to `pannpers@pannpers.dev` of at most 2,000 characters
- **AND** its subject SHALL contain the Error ID
- **AND** spaces in the subject and body SHALL be encoded as `%20`, not `+`

#### Scenario: Dismiss clears current error
- **WHEN** `dismiss` is called
- **THEN** `currentError` SHALL be set to `null`

## REMOVED Requirements

### Requirement: Error Banner UI in Root Component
**Reason**: Its "Report to GitHub" button sent fans to a public issue tracker, and "Copy Error Details" is no longer offered: the error report reaches the team directly, and the email carries the details the team needs. Replaced by "Error banner offers reload, close and an email report". A scenario cannot be dropped or renamed inside a MODIFIED block, so the requirement is replaced.
**Migration**: None for users. Tests that cite this requirement's scenarios cite the new requirement's.

### Requirement: Error boundary service captures and sanitizes errors
**Reason**: Its scenario "GitHub issue URL is constructed correctly" described the GitHub link, and its redaction scenario named the Markdown report, which is removed. Replaced by "Error boundary service captures errors and builds the report email", which keeps the other scenarios word for word.
**Migration**: None for users. Tests that cite this requirement's scenarios cite the new requirement's.
