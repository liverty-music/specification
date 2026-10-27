# components/infrastructure/fan/web/route/delete-account Specification

## Purpose
The fan's withdrawal screen, opened from Settings, where a signed-in fan sees what stops their account from being deleted, learns what deletion means, signs in again and deletes their account.

## Requirements

### Requirement: The screen shows what blocks deletion

On opening, the screen SHALL read the fan's deletion blockers through UserService.ListDeletionBlockers. While any blocker is returned, the screen SHALL list each one with its count in the fan's language (for example 「開催前の公演のチケット 2 枚」, 「出品中のリセール 1 件」, 「抽選待ちの応募 1 件」, 「手続き中の購入 1 件」), say that the account can be deleted once they are finished, and SHALL NOT offer the delete control. When the read fails, the screen SHALL show the error with a retry control and SHALL NOT offer the delete control.

#### Scenario: Fan with an upcoming ticket

- **WHEN** a fan holding two Tickets for a concert next week opens the withdrawal screen
- **THEN** the screen lists 「開催前の公演のチケット 2 枚」 and offers no delete control

#### Scenario: Read fails

- **WHEN** UserService.ListDeletionBlockers fails with Unavailable
- **THEN** the screen shows the error and a retry control, and offers no delete control

### Requirement: The screen states what deletion means

When no blocker is returned, the screen SHALL state, before the delete control: that the account and its follows, notification settings, passkeys and identity check (本人確認) result are removed; that purchase history and past tickets can no longer be viewed; that this cannot be undone; that signing up again with the same email address starts a new, empty account; and that transaction records are kept as the Privacy Policy describes, with a link to the in-app Privacy Policy.

#### Scenario: Fan with nothing in progress

- **WHEN** a fan with no blocker opens the withdrawal screen
- **THEN** the screen shows each of these statements, the Privacy Policy link and a delete control

### Requirement: Deleting asks for a fresh sign-in

Activating the delete control SHALL open a modal confirmation dialog whose Cancel control receives initial focus; Cancel and Escape SHALL close it without deleting. Confirming SHALL send the fan to the hosted login to sign in again with a passkey and return them to the withdrawal screen, the same fresh sign-in passkey management uses, and the app SHALL then call UserService.Delete with the proof of that sign-in. The proof SHALL be kept in memory only and dropped once the call returns or the fan leaves the screen. When the fresh sign-in is abandoned or fails, or names a different account from the signed-in fan, UserService.Delete SHALL NOT be called and the screen SHALL say the account was not deleted.

#### Scenario: Fan confirms

- **WHEN** a fan with no blocker activates delete, confirms, and signs in again with their passkey
- **THEN** UserService.Delete is called once for the fan

#### Scenario: Fan cancels

- **WHEN** the fan activates delete and then presses Escape
- **THEN** the dialog closes, no sign-in is asked for and UserService.Delete is not called

#### Scenario: Fresh sign-in abandoned

- **WHEN** the fan closes the hosted login without signing in
- **THEN** the fan returns to the withdrawal screen, which says the account was not deleted

#### Scenario: Different account

- **WHEN** the fresh sign-in names an account other than the signed-in fan's
- **THEN** UserService.Delete is not called and the screen says the account was not deleted

### Requirement: After deletion the fan leaves signed out

When UserService.Delete succeeds, the app SHALL clear the fan's sign-in session, stop identifying the fan to analytics on this device, and show a screen saying the account was deleted, from which the fan can go to the Welcome screen. When it fails with FailedPrecondition, the screen SHALL read the blockers again and show them; any other failure SHALL be shown with a retry control and the fan stays signed in.

#### Scenario: Deletion succeeds

- **WHEN** UserService.Delete succeeds
- **THEN** the fan is signed out, the deleted-account message is shown, and later analytics events on this device are not tied to the deleted account

#### Scenario: Ticket bought in another tab

- **WHEN** UserService.Delete fails with FailedPrecondition because the fan bought a ticket elsewhere meanwhile
- **THEN** the screen lists the new blocker and offers no delete control
