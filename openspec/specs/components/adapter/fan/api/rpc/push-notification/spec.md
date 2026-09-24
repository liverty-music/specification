# Push Notification RPC

## Purpose

The fan-facing push notification service boundary: who may register, check and remove a browser's push subscription, who may trigger new-concert pushes directly, and what the boundary itself decides before PushNotificationUseCase runs.

## Requirements

### Requirement: Registering a browser is always for the caller

Create SHALL register the browser for the signed-in caller, resolved to their stored User (User.GetByExternalID); the request names no fan. It SHALL fail with Unauthenticated when the caller is not signed in, with NotFound when the caller has no account, and with InvalidArgument when the push address or the keys are missing or not well formed.

#### Scenario: Fan registers their browser

- **WHEN** a signed-in fan calls Create with their browser's push address and keys
- **THEN** PushNotificationUseCase.Create runs for that fan

#### Scenario: Missing keys

- **WHEN** Create is called without keys
- **THEN** it fails with InvalidArgument

#### Scenario: Not signed in

- **WHEN** the caller is not authenticated
- **THEN** Create fails with Unauthenticated

### Requirement: Checking and removing a browser only for the caller

Get and Delete SHALL resolve the signed-in caller to their stored User and require the fan named in the request to be that caller. They SHALL fail with Unauthenticated when the caller is not signed in, with NotFound when the caller has no account, with InvalidArgument when no fan or no push address is given, and with PermissionDenied when the named fan is not the caller, before anything is read or removed, so a caller learns nothing about another fan's browsers.

#### Scenario: Fan checks their browser

- **WHEN** a signed-in fan calls Get naming themselves and their push address
- **THEN** PushNotificationUseCase.Get runs for that fan

#### Scenario: Request names another fan

- **WHEN** Get or Delete names a fan other than the caller
- **THEN** it fails with PermissionDenied, nothing is removed, and nothing reveals whether that fan has the browser

#### Scenario: Missing push address

- **WHEN** Delete is called without a push address
- **THEN** it fails with InvalidArgument

### Requirement: Direct new-concert push only outside production

NotifyNewConcerts SHALL be callable only by a signed-in caller and only when the server does not run in production. It SHALL fail with Unauthenticated when the caller is not signed in, whatever the environment, so an unauthenticated caller cannot learn the environment. In production it SHALL fail with PermissionDenied whatever the caller's credentials, and nothing is sent. It SHALL fail with InvalidArgument when no artist is given, when no concert is given, when more than 1000 concerts are given, or when a concert id is empty. Otherwise it SHALL run PushNotificationUseCase.NotifyNewConcerts with the artist and exactly the given concerts and return once it completes.

#### Scenario: Non-production call

- **WHEN** a signed-in caller calls NotifyNewConcerts with an artist and 2 concerts on a non-production server
- **THEN** NotifyNewConcerts runs for those 2 concerts and the call succeeds after it completes

#### Scenario: Production

- **WHEN** NotifyNewConcerts is called on the production server
- **THEN** it fails with PermissionDenied and nobody is notified

#### Scenario: Not signed in

- **WHEN** an unauthenticated caller calls NotifyNewConcerts
- **THEN** it fails with Unauthenticated in every environment

#### Scenario: No concerts

- **WHEN** NotifyNewConcerts is called with no concert
- **THEN** it fails with InvalidArgument

#### Scenario: Too many concerts

- **WHEN** NotifyNewConcerts is called with 1001 concerts
- **THEN** it fails with InvalidArgument
