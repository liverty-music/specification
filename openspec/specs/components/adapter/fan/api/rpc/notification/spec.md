# Notification RPC

## Purpose

The fan-facing notification service boundary: who may mark a notification read or dismissed, and what the boundary itself decides before NotificationUseCase runs.

## Requirements

### Requirement: Read and dismiss act only for the signed-in caller

MarkRead and MarkDismissed SHALL resolve the signed-in caller to their stored User (User.GetByExternalID) and require the fan named in the request to be that caller. They SHALL fail with Unauthenticated when the caller is not signed in, with NotFound when the caller has no account, with InvalidArgument when no fan or no notification is given, and with PermissionDenied when the named fan is not the caller, before any Notification changes.

#### Scenario: Fan marks their notification read

- **WHEN** a signed-in fan calls MarkRead naming themselves and one of their Notifications
- **THEN** NotificationUseCase.MarkRead runs for that fan

#### Scenario: Request names another fan

- **WHEN** the request names a fan other than the caller
- **THEN** the call fails with PermissionDenied and nothing changes

#### Scenario: Not signed in

- **WHEN** the caller is not authenticated
- **THEN** the call fails with Unauthenticated

#### Scenario: Missing notification

- **WHEN** no notification is given
- **THEN** the call fails with InvalidArgument
