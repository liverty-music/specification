# Spec Delta

## MODIFIED Requirements

### Requirement: One card authorization per purchase

CardAuthorization.Create SHALL take the purchase it is for and an amount in whole yen. The purchase is a Checkout, with its Order's user, TicketStock and ticket count, or a lottery entry, given by its user, Lottery TicketSale, TicketStock, ticket count and optional ReferralCode. It SHALL open a Pending CardAuthorization for that amount that carries the purchase and charges nothing until CardAuthorization.Capture runs. It SHALL return the CardAuthorization and its card authorization secret, which SHALL NOT be stored. Repeating it for the same Checkout SHALL return the same CardAuthorization and open no second one; each call for a lottery entry SHALL open a new one. It SHALL fail with InvalidArgument when the amount is zero or negative, and with Unavailable when the payment provider cannot be reached.

#### Scenario: Card authorization opened
- **WHEN** CardAuthorization.Create is called for a 6000 yen Checkout
- **THEN** a Pending 6000 yen card authorization carrying the Checkout is opened, it and its card authorization secret are returned, and nothing is charged

#### Scenario: Retried after a lost response
- **WHEN** CardAuthorization.Create is called again for the same Checkout
- **THEN** the same card authorization is returned and no second one is opened

#### Scenario: Lottery entry authorized again
- **WHEN** CardAuthorization.Create is called for a lottery entry of 2 tickets and then of 3 tickets of the same fan, sale and TicketStock
- **THEN** two card authorizations are opened, each carrying its own ticket count

#### Scenario: Non-positive amount
- **WHEN** CardAuthorization.Create is called with an amount of zero or less
- **THEN** it fails with InvalidArgument and no card authorization is opened

#### Scenario: Payment provider unavailable
- **WHEN** the payment provider cannot be reached
- **THEN** CardAuthorization.Create fails with Unavailable
