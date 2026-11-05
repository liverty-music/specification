# Spec Delta

## MODIFIED Requirements

### Requirement: Delete a stock no live order names

Delete SHALL remove the TicketStock with the given id together with the Void Orders that name it, their LotteryEntries, Checkouts and ResaleEntries and their CardAuthorizations, all together or not at all. It SHALL fail with FailedPrecondition, removing nothing, when an Order that is not Void names the TicketStock, also one created while Delete runs, and with NotFound when no TicketStock has the id. A Void Order whose card authorization is not yet released does not keep the TicketStock.

#### Scenario: Stock without orders
- **WHEN** Delete is called for a TicketStock no Order names
- **THEN** the TicketStock is removed

#### Scenario: Stock with an abandoned checkout
- **WHEN** the only Order naming the TicketStock is Void, its Checkout Expired
- **THEN** the TicketStock, the Void Order and its Checkout are removed

#### Scenario: Void order with a card authorization not yet released
- **WHEN** the only Order naming the TicketStock is Void and its card authorization is not yet released
- **THEN** the TicketStock, the Void Order and its Checkout are removed

#### Scenario: Stock with a pending order
- **WHEN** an Order naming the TicketStock is Pending
- **THEN** Delete fails with FailedPrecondition and nothing is removed

#### Scenario: Stock with a paid order
- **WHEN** an Order naming the TicketStock is Paid
- **THEN** Delete fails with FailedPrecondition and nothing is removed

#### Scenario: Unknown id
- **WHEN** no TicketStock has the id
- **THEN** Delete fails with NotFound
