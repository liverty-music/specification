# components/infrastructure/admin/web/global/error-messages Specification

## Purpose
How every admin console screen reports a failed call to the admin: with copy the console owns, chosen from the error code and the operation that failed, never with the server's or a library's error text.

## Requirements

### Requirement: A failed call shows copy the console owns

When a call from any admin console screen fails, the screen SHALL show copy the admin console owns, chosen from the error code and, where the screen knows it, the operation that failed. It SHALL NOT show the error message the server sent or the text of an error raised in the browser. An error code the screen has no copy for, and a failure that carries no error code (the network is down, the response cannot be read), SHALL show the screen's copy for that operation failing. The console SHALL record the failed call, with the server's message, in the browser console log.

#### Scenario: Server message stays off the screen

- **WHEN** Approve on the approval queue fails with Internal and the message `begin transaction: connection reset (internal)`
- **THEN** the row shows `Approval failed. Try again.`, the text `connection reset` appears nowhere on the screen, and the browser console log has the message

#### Scenario: Failure without an error code

- **WHEN** loading the published concerts fails because the network is down
- **THEN** the screen shows `Failed to load published concerts.`

#### Scenario: Code without copy of its own

- **WHEN** Delete on the published concerts screen fails with InvalidArgument and the message `event_id: value must be a valid UUID`
- **THEN** the row shows `Delete failed. Try again.` and not the server's message

### Requirement: A form the screen checks shows fixed copy for InvalidArgument

When a call sent from a form whose fields the screen checks before sending fails with InvalidArgument, the screen SHALL show `The request was invalid. Check the fields.`, unless the screen's own requirements give that operation other copy.

#### Scenario: Business details refused by the server

- **WHEN** saving an Organizer's business details fails with InvalidArgument and the message `business phone number is invalid (invalid_argument)`
- **THEN** the form shows `The request was invalid. Check the fields.` and not the server's message

### Requirement: An expired session shows that sign-in is being renewed

When a call fails with Unauthenticated, the screen SHALL show `Your session expired — signing you back in…` in place of the operation's failure copy.

#### Scenario: Session expired during a call

- **WHEN** loading the approval queue fails with Unauthenticated
- **THEN** the screen shows `Your session expired — signing you back in…`

### Requirement: A failed sign-in shows fixed copy

When completing sign-in fails and the admin has no session, the sign-in callback page SHALL show `Sign-in failed. Return to the console and sign in again.` and a link back to the console, and SHALL NOT show the error's own text.

#### Scenario: Sign-in callback fails

- **WHEN** completing sign-in fails with the error `No matching state found in storage`
- **THEN** the page shows `Sign-in failed. Return to the console and sign in again.` and the link, and the error's text is not shown
