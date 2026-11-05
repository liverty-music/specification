# Spec Delta

## Purpose

Finds a CardAuthorization by the payment provider's ID for it, so a notice from the payment provider, which names only that ID, reaches the card authorization.

## ADDED Requirements

### Requirement: Find a card authorization by the payment provider's ID

CardAuthorization.GetByProviderCardAuthorizationID SHALL return the same CardAuthorization as CardAuthorization.Get for the CardAuthorization whose provider card authorization ID is the given one. It SHALL fail with NotFound when no CardAuthorization has that provider card authorization ID, and with Unavailable when the payment provider cannot be reached.

#### Scenario: Notice for a known card authorization
- **WHEN** the payment provider's ID of an Authorized card authorization opened for a resale entry is looked up
- **THEN** that card authorization is returned, Authorized, with its own id, its purchase and its expiry time

#### Scenario: Unknown provider ID
- **WHEN** no card authorization has the payment provider's ID
- **THEN** CardAuthorization.GetByProviderCardAuthorizationID fails with NotFound

#### Scenario: Payment provider unavailable
- **WHEN** the payment provider cannot be reached
- **THEN** CardAuthorization.GetByProviderCardAuthorizationID fails with Unavailable
