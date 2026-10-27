## MODIFIED Requirements

### Requirement: Payout clawed back

Refund SHALL read the Order's Settlement with Settlement.GetByOrderID; every Order has one, and a failure to read it SHALL be returned with no money moved and nothing recorded. When the Settlement is Released, Refund SHALL reverse every paid split that is not yet reversed with Settlement.ReversePayout for the split's amount. When it is Held, no payout is reversed and the Settlement becomes Reversed, so it is never paid out later. When it is already Reversed, as after every Ticket of the Order was resold, nothing is clawed back and no Settlement is given to Order.CommitRefund. Only the paid splits are reversed: the platform fee was never paid out, so it is not recovered from the Organizer, and when a Released Order is refunded — in practice a Dispute that arrives after the release — the platform bears its fee.

#### Scenario: Payout already released

- **WHEN** the Order's Settlement is Released
- **THEN** each paid split is reversed and the Settlement becomes Reversed

#### Scenario: Payout not yet released

- **WHEN** the Order's Settlement is Held
- **THEN** no payout is reversed and the Settlement becomes Reversed

#### Scenario: Settlement given up by resales

- **WHEN** the Order's Settlement was Reversed because every Ticket was resold
- **THEN** nothing is clawed back and the Order is recorded Refunded

#### Scenario: Settlement unreadable

- **WHEN** Settlement.GetByOrderID fails with NotFound
- **THEN** Refund fails with NotFound, no money moves and the Order stays Paid
