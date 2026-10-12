# Notification RPC

## Purpose

The fan-facing notification service boundary: who may mark a notification read or dismissed, and what the boundary itself decides before NotificationUseCase runs.

## Requirements

### Requirement: Read and dismiss act for the signed-in caller

MarkRead and Dismiss SHALL act for the signed-in caller, resolved to their stored User (User.GetByProviderUserID); the request names no fan. MarkRead SHALL hand that User and the notification to NotificationUseCase.MarkRead, and Dismiss to NotificationUseCase.Dismiss, which refuse a Notification of another fan. They SHALL fail with Unauthenticated when the caller is not signed in, with NotFound when the caller has no account, and with InvalidArgument when no notification is given, before any Notification changes.

#### Scenario: Fan marks their notification read

- **WHEN** a signed-in fan calls MarkRead with one of their Notifications
- **THEN** NotificationUseCase.MarkRead runs for that fan

#### Scenario: Fan dismisses their notification

- **WHEN** a signed-in fan calls Dismiss with one of their Notifications
- **THEN** NotificationUseCase.Dismiss runs for that fan

#### Scenario: Not signed in

- **WHEN** the caller is not authenticated
- **THEN** the call fails with Unauthenticated

#### Scenario: Missing notification

- **WHEN** no notification is given
- **THEN** the call fails with InvalidArgument
