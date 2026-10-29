## MODIFIED Requirements

### Requirement: An Order with its Settlement

GetWithSettlement SHALL read the Order with Order.Get, failing with NotFound when it does not exist. For a Pending or Void Order, which was never paid, it SHALL return the Order alone. For a Paid or Refunded Order it SHALL read its Settlement with Settlement.GetByOrderID and return both; every such Order has a Settlement, and a failure to read it, NotFound included, SHALL be returned as Internal, so it is not taken for a missing Order. Other failures SHALL be returned unchanged.

#### Scenario: Order with a held settlement
- **WHEN** a Paid Order's payout is Held
- **THEN** GetWithSettlement returns the Order and its Held Settlement with its splits

#### Scenario: Order with no settlement yet
- **WHEN** the Order is Pending
- **THEN** GetWithSettlement returns the Order and no Settlement, without reading one

#### Scenario: Order not found
- **WHEN** no Order has the id
- **THEN** GetWithSettlement fails with NotFound

#### Scenario: Settlement missing
- **WHEN** Settlement.GetByOrderID fails with NotFound for a Paid Order
- **THEN** GetWithSettlement fails with Internal
