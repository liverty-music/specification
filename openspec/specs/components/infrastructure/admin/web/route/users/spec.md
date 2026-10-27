# components/infrastructure/admin/web/route/users Specification

## Purpose
The admin console's Users screen, where an admin finds one fan's account by email address, sees what blocks its deletion and deletes it at the fan's request.

## Requirements

### Requirement: An admin finds a fan by email

The Users screen SHALL offer one email address field. Submitting it SHALL call UserService.GetByEmail and show the returned User's name, email address, id and deletion blockers, each with its count. An unregistered address SHALL show that no account has that address; any other failure SHALL be shown with its error. The screen SHALL list no Users other than the one found.

#### Scenario: Registered fan

- **WHEN** the admin submits `fan@example.com` and a fan has that address
- **THEN** the screen shows that fan's name, `fan@example.com`, id and their blockers

#### Scenario: Unregistered address

- **WHEN** UserService.GetByEmail fails with NotFound
- **THEN** the screen says no account has that address and offers no Delete control

### Requirement: Delete is offered only without blockers and asks for confirmation

The screen SHALL offer Delete only when the found User has no blocker. Activating Delete SHALL open a modal confirmation dialog that names the User by name and email address and says the account is removed permanently while order and ticket records remain. The Cancel control SHALL receive initial focus; Cancel and Escape SHALL close the dialog without deleting. UserService.Delete SHALL be called only when the admin activates the dialog's Delete control, and that control SHALL be disabled while the call is in flight.

#### Scenario: Fan with an upcoming ticket

- **WHEN** the found User has an Upcoming ticket blocker
- **THEN** the screen shows the blocker and offers no Delete control

#### Scenario: Admin confirms

- **WHEN** the admin activates Delete for a User with no blocker and then the dialog's Delete control
- **THEN** UserService.Delete is called once for that User

#### Scenario: Admin cancels

- **WHEN** the admin activates Delete and then presses Escape
- **THEN** the dialog closes and UserService.Delete is not called

### Requirement: Delete's outcome is shown

When UserService.Delete succeeds, the screen SHALL say the account was deleted and clear the found User. When it fails with FailedPrecondition, the screen SHALL fetch the User again and show its blockers; any other failure SHALL be shown with its error and the User stays shown.

#### Scenario: Deleted

- **WHEN** UserService.Delete succeeds
- **THEN** the screen says the account was deleted and no User is shown

#### Scenario: Blocker appeared meanwhile

- **WHEN** UserService.Delete fails with FailedPrecondition
- **THEN** the screen shows the User's current blockers and offers no Delete control
