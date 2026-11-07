## MODIFIED Requirements

### Requirement: Read and dismiss act for the signed-in caller

List and MarkRead SHALL act for the signed-in caller, resolved to their stored User (User.GetByProviderUserID); the request names no fan. List SHALL hand that User to NotificationUseCase.List and return the Notifications it returns, each with its rendered title, body and link, its type, its create time and its read time when read. MarkRead SHALL hand that User and the notification to NotificationUseCase.MarkRead, which refuses a Notification of another fan. They SHALL fail with Unauthenticated when the caller is not signed in and with NotFound when the caller has no account; MarkRead SHALL fail with InvalidArgument when no notification is given, before any Notification changes.

#### Scenario: Fan lists their notifications

- **WHEN** a signed-in fan calls List
- **THEN** NotificationUseCase.List runs for that fan and its Notifications are returned

#### Scenario: Fan marks their notification read

- **WHEN** a signed-in fan calls MarkRead with one of their Notifications
- **THEN** NotificationUseCase.MarkRead runs for that fan

#### Scenario: Fan dismisses their notification

- **WHEN** a client calls Dismiss
- **THEN** the service has no Dismiss method and no Notification changes

#### Scenario: Not signed in

- **WHEN** the caller is not authenticated
- **THEN** the call fails with Unauthenticated

#### Scenario: Missing notification

- **WHEN** MarkRead is called with no notification
- **THEN** the call fails with InvalidArgument
