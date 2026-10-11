# Spec Delta

## Purpose

The fan-facing order service boundary: a fan reads only their own Orders, and the Order's user is always the signed-in caller.

## ADDED Requirements

### Requirement: A fan reads their own order

Get SHALL require a signed-in caller and fail with Unauthenticated otherwise. It SHALL resolve the caller to their stored User (User.GetByExternalID) and pass that User and the requested Order to TicketUseCase.GetOrder; the request never names a user. When the caller has no stored account, the call SHALL fail with NotFound. Get SHALL fail with InvalidArgument when no order is given.

#### Scenario: Fan reads their order

- **WHEN** a signed-in fan calls Get with the id of their own Order
- **THEN** that Order is returned

#### Scenario: Not signed in

- **WHEN** a caller who is not signed in calls Get
- **THEN** the call fails with Unauthenticated

#### Scenario: Missing order

- **WHEN** Get is called without an order
- **THEN** it fails with InvalidArgument
