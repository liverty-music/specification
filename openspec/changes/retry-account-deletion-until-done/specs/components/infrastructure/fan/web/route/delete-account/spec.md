# Spec Delta

## MODIFIED Requirements

### Requirement: After deletion the fan leaves signed out

When UserService.Delete succeeds, or fails with NotFound because an earlier deletion has completed, the app SHALL clear the fan's sign-in session, stop identifying the fan to analytics on this device, and show a screen saying the account was deleted, from which the fan can go to the Welcome screen. When it fails with FailedPrecondition, the screen SHALL read the blockers again and show them; any other failure SHALL be shown with a retry control and the fan stays signed in.

#### Scenario: Deletion succeeds

- **WHEN** UserService.Delete succeeds
- **THEN** the fan is signed out, the deleted-account message is shown, and later analytics events on this device are not tied to the deleted account

#### Scenario: Ticket bought in another tab

- **WHEN** UserService.Delete fails with FailedPrecondition because the fan bought a ticket elsewhere meanwhile
- **THEN** the screen lists the new blocker and offers no delete control

#### Scenario: Retry after the deletion completed

- **WHEN** UserService.Delete failed with Unavailable, the fan retries, and it fails with NotFound
- **THEN** the fan is signed out and the deleted-account message is shown
