# Spec Delta

## Purpose

The organizer console's single place for the result of an action: a short message at the bottom of the window that confirms a save or reports a failure with a way to retry, without moving the page.

## ADDED Requirements

### Requirement: One snackbar at a time, at the bottom of the window

The console SHALL show the result of an action (saved, published, link issued, failed) in one snackbar area at the bottom of the window, above the navigation bar on a phone. A new message SHALL replace the one shown. The snackbar SHALL be announced to screen readers without moving the keyboard focus, and SHALL never cover a dialog's buttons.

#### Scenario: Two results in a row

- **WHEN** an operator saves a concert and then copies a share link within 2 seconds
- **THEN** the save message is replaced by the copy message and only one snackbar is shown

#### Scenario: Phone layout

- **WHEN** a snackbar appears on a 390 px wide phone
- **THEN** it sits above the navigation bar and does not hide it

### Requirement: Success disappears, an error with Retry stays

A message without an action SHALL disappear after 4 seconds. A message with an action other than Retry SHALL disappear after 10 seconds. A failure the operator can retry SHALL show a Retry action and SHALL stay until the operator retries or dismisses it. Every snackbar SHALL offer a close button. Pressing Retry SHALL repeat the failed action once and dismiss the snackbar.

#### Scenario: Save succeeded

- **WHEN** an operator saves a concert and the save succeeds
- **THEN** a snackbar says 変更を保存しました and disappears after 4 seconds

#### Scenario: Save failed

- **WHEN** a save fails because the network is down
- **THEN** a snackbar says the save failed, offers 再試行 (Retry), and stays until the operator presses 再試行 or closes it

#### Scenario: Operator retries

- **WHEN** the operator presses 再試行 on a failed save
- **THEN** the save runs again once and the snackbar closes

### Requirement: Field errors never go to the snackbar

An error about one form field (a missing name, a window that is too long) SHALL be shown next to that field and SHALL NOT be shown in the snackbar.

#### Scenario: Missing sale name

- **WHEN** an operator saves a lottery sale without a name
- **THEN** the error is shown under the name field and no snackbar appears
