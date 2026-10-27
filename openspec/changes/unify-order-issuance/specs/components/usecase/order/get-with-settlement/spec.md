## REMOVED Requirements

### Requirement: An Order with its Settlement
**Reason**: Every Order is issued together with its Settlement (components/entity/order/issue), so the case of an Order without one is gone.
**Migration**: Replaced by "An Order and its Settlement", which returns a failure to read the Settlement.

## ADDED Requirements

### Requirement: An Order and its Settlement

GetWithSettlement SHALL read the Order with Order.Get, failing with NotFound when it does not exist, then read its Settlement with Settlement.GetByOrderID and return both. Every Order has a Settlement; a failure to read it, NotFound included, SHALL be returned as Internal, so it is not taken for a missing Order. Other failures SHALL be returned unchanged.

#### Scenario: Order with a held settlement
- **WHEN** an Order's payout is Held
- **THEN** GetWithSettlement returns the Order and its Held Settlement with its splits

#### Scenario: Order not found
- **WHEN** no Order has the id
- **THEN** GetWithSettlement fails with NotFound

#### Scenario: Settlement missing
- **WHEN** Settlement.GetByOrderID fails with NotFound for an existing Order
- **THEN** GetWithSettlement fails with Internal
