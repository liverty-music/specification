# components/entity/card-authorization/create Specification

## Purpose
Opens a CardAuthorization in yen for the amount of one purchase, a LotteryEntry or a Checkout, at most once per purchase, and returns it with the secret the fan's browser uses to complete card authentication; nothing is charged.

## Requirements

### Requirement: One card authorization per purchase

CardAuthorization.Create SHALL take the purchase it is for, a LotteryEntry or a Checkout, and an amount in whole yen, and open a Pending CardAuthorization for that amount that charges nothing until CardAuthorization.Capture runs. It SHALL return the CardAuthorization and its card authorization secret, which SHALL NOT be stored. Repeating it for the same purchase SHALL return the same CardAuthorization and open no second one. It SHALL fail with InvalidArgument when the amount is zero or negative, and with Unavailable when the payment provider cannot be reached.

#### Scenario: Card authorization opened
- **WHEN** CardAuthorization.Create is called for a 6000 yen Checkout
- **THEN** a Pending 6000 yen card authorization is opened, it and its card authorization secret are returned, and nothing is charged

#### Scenario: Retried after a lost response
- **WHEN** CardAuthorization.Create is called again for the same LotteryEntry
- **THEN** the same card authorization is returned and no second one is opened

#### Scenario: Non-positive amount
- **WHEN** CardAuthorization.Create is called with an amount of zero or less
- **THEN** it fails with InvalidArgument and no card authorization is opened

#### Scenario: Payment provider unavailable
- **WHEN** the payment provider cannot be reached
- **THEN** CardAuthorization.Create fails with Unavailable
