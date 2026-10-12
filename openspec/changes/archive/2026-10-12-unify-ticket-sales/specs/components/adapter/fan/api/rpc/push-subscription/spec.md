# Spec Delta

## Purpose

The fan-facing push subscription service boundary: a signed-in fan registers, checks and removes only their own browsers' push subscriptions, and the boundary rejects malformed requests before PushSubscriptionUseCase runs.

## ADDED Requirements

### Requirement: Registering a browser is always for the caller

Create SHALL register the browser for the signed-in caller, resolved to their stored User (User.GetByProviderUserID); the request names no fan. It SHALL fail with Unauthenticated when the caller is not signed in, with NotFound when the caller has no account, and with InvalidArgument when the push address or the keys are missing or not well formed.

#### Scenario: Fan registers their browser

- **WHEN** a signed-in fan calls Create with their browser's push address and keys
- **THEN** PushSubscriptionUseCase.Create runs for that fan

#### Scenario: Missing keys

- **WHEN** Create is called without keys
- **THEN** it fails with InvalidArgument

#### Scenario: Not signed in

- **WHEN** the caller is not authenticated
- **THEN** Create fails with Unauthenticated

### Requirement: Checking and removing a browser only for the caller

Get and Delete SHALL take the browser's push address, which identifies the subscription, and act only on the signed-in caller's own subscriptions, resolved to their stored User (User.GetByProviderUserID); the request names no fan. They SHALL fail with Unauthenticated when the caller is not signed in, with NotFound when the caller has no account, and with InvalidArgument when no push address is given. Get SHALL answer NotFound for a push address the caller has not registered, whoever else has, and Delete SHALL remove nothing then, so a caller learns nothing about another fan's browsers.

#### Scenario: Fan checks their browser

- **WHEN** a signed-in fan calls Get with their push address
- **THEN** PushSubscriptionUseCase.Get runs for that fan

#### Scenario: Push address of another fan

- **WHEN** a signed-in fan calls Get or Delete with a push address that only another fan has registered
- **THEN** Get fails with NotFound, Delete removes nothing, and nothing reveals whether that fan has the browser

#### Scenario: Missing push address

- **WHEN** Delete is called without a push address
- **THEN** it fails with InvalidArgument
