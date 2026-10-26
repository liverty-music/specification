## ADDED Requirements

### Requirement: Admins list the orders of an event

ListByEvent SHALL require a signed-in caller holding the admin role. A caller who is not signed in SHALL fail with Unauthenticated; a signed-in caller without the admin role SHALL fail with PermissionDenied; both checks come before anything is read. ListByEvent SHALL fail with InvalidArgument when no Event is given or its id is malformed. Otherwise it SHALL run OrderUseCase.ListByEvent and return the Orders, each with its id, user, status, amount, currency and pay time.

#### Scenario: Admin lists an event's orders

- **WHEN** a signed-in admin calls ListByEvent for an Event with one Paid Order
- **THEN** that Order is returned with its status Paid and its amount

#### Scenario: Event missing

- **WHEN** an admin calls ListByEvent without an Event id
- **THEN** it fails with InvalidArgument

#### Scenario: Non-admin lists orders

- **WHEN** a signed-in caller without the admin role calls ListByEvent
- **THEN** the call fails with PermissionDenied and nothing is returned
