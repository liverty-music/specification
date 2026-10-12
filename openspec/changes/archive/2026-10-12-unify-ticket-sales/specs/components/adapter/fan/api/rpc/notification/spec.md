# Spec Delta

## ADDED Requirements

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

## REMOVED Requirements

### Requirement: Read and dismiss act only for the signed-in caller
**Reason**: The request no longer names the calling fan; the fan is taken from the sign-in (design D15), so the check that the named fan is the caller goes with the field. MarkDismissed is renamed Dismiss under the RPC naming rule.
**Migration**: The behavior continues in "Read and dismiss act for the signed-in caller" above; clients call `MarkRead` and `Dismiss` without a user id.
