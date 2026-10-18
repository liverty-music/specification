# Spec Delta

## Purpose

How every organizer console screen reports a failed call to the member: in the snackbar, next to a form or on the sign-in callback page, with copy the console owns in the member's language, never with the server's or a library's error text.

## ADDED Requirements

### Requirement: A failed call shows copy the console owns

When a call from any organizer console screen fails, the screen SHALL show copy from the console's own catalog in the member's language, chosen from the error code and the operation that failed, in the snackbar or next to the form that sent it. It SHALL NOT show the error message the server sent or the text of an error raised in the browser. An error code the screen has no copy for, and a failure that carries no error code, SHALL show the screen's copy for that operation failing. The console SHALL record the failed call, with the server's message, in the browser console log.

#### Scenario: Refused first-come sale save

- **WHEN** saving a first-come sale fails with FailedPrecondition and the message `ticket sale window overlaps another sale (failed_precondition)`
- **THEN** the page shows 保存できませんでした。 followed by the console's list of what to check, the server's message appears nowhere on the page, and the browser console log has it

#### Scenario: Publish fails without copy of its own

- **WHEN** publishing an event fails with Internal and the message `publish series: deadline exceeded (internal)`
- **THEN** the snackbar says 公開できませんでした with 再試行 (Retry), and not the server's message

### Requirement: A failed sign-in shows fixed copy

When completing sign-in fails, the member has no session and the console does not restart sign-in itself, the sign-in callback page SHALL show サインインできませんでした。 (Could not sign in.) and もう一度サインインする (Sign in again), and SHALL NOT show the error's own text.

#### Scenario: Sign-in callback fails

- **WHEN** completing sign-in fails with the error `invalid_grant: code expired` and the member has no session
- **THEN** the page shows サインインできませんでした。 and もう一度サインインする, and `invalid_grant` is not shown
