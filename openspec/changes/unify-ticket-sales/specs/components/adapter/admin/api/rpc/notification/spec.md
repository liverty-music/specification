# Spec Delta

## Purpose

The admin-facing notification service boundary: who may trigger new-concert pushes directly, a test hook that runs only outside production, and what the boundary checks before PushNotificationUseCase runs.

## ADDED Requirements

### Requirement: Direct new-concert push only outside production

NotifyNewConcerts SHALL be callable only by a signed-in caller holding the admin role and only when the server does not run in production. It SHALL fail with Unauthenticated when the caller is not signed in, whatever the environment, so an unauthenticated caller cannot learn the environment, and with PermissionDenied when the caller lacks the admin role. In production it SHALL fail with PermissionDenied whatever the caller's credentials, and nothing is sent. It SHALL fail with InvalidArgument when no artist is given, when no concert is given, when more than 1000 concerts are given, or when a concert id is empty. Otherwise it SHALL run PushNotificationUseCase.NotifyNewConcerts with the artist and exactly the given concerts and return once it completes.

#### Scenario: Non-production call

- **WHEN** a signed-in admin calls NotifyNewConcerts with an artist and 2 concerts on a non-production server
- **THEN** NotifyNewConcerts runs for those 2 concerts and the call succeeds after it completes

#### Scenario: Production

- **WHEN** NotifyNewConcerts is called on the production server
- **THEN** it fails with PermissionDenied and nobody is notified

#### Scenario: Not signed in

- **WHEN** an unauthenticated caller calls NotifyNewConcerts
- **THEN** it fails with Unauthenticated in every environment

#### Scenario: Caller without the admin role

- **WHEN** a signed-in caller without the admin role calls NotifyNewConcerts on a non-production server
- **THEN** it fails with PermissionDenied and nobody is notified

#### Scenario: No concerts

- **WHEN** NotifyNewConcerts is called with no concert
- **THEN** it fails with InvalidArgument

#### Scenario: Too many concerts

- **WHEN** NotifyNewConcerts is called with 1001 concerts
- **THEN** it fails with InvalidArgument
