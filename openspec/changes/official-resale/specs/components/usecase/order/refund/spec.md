## MODIFIED Requirements

### Requirement: Fan refunded the full amount

For the reason Cancellation, Refund SHALL refund the price of the Order's Tickets that are still Issued — the Order's amount divided by its number of Tickets, times the number still Issued — to the fan's original payment with Order.CreateRefund for the Order's own refund, against the charge recorded on the Order's Settlement or, when none is recorded, the charge found by Order.GetProviderChargeID. Tickets the fan resold through official resale were already refunded less the resale fee and are not refunded again. When no Ticket of the Order is Issued, it SHALL issue no refund. It SHALL fail with FailedPrecondition when the Order's payment provider cannot issue refunds or the Order has no provider payment ID. For the reason Dispute it SHALL issue no refund, because the dispute has already returned the money to the fan.

#### Scenario: Cancellation refund

- **WHEN** an event is cancelled and a 16000 yen Order is refunded with the reason Cancellation
- **THEN** 16000 yen is refunded to the fan's card

#### Scenario: Cancellation after a resale

- **WHEN** an event is cancelled and a 10000 yen Order for 2 tickets, one of which was resold, is refunded with the reason Cancellation
- **THEN** 5000 yen is refunded to the fan's card

#### Scenario: Every ticket resold

- **WHEN** an event is cancelled and every Ticket of the Order was resold
- **THEN** no refund is issued and the Order is recorded Refunded

#### Scenario: Dispute

- **WHEN** Refund runs with the reason Dispute
- **THEN** no refund is issued to the fan and the rest of the refund still happens

### Requirement: Payout clawed back

When the Order's Settlement, read with Settlement.GetByOrderID, is Released, Refund SHALL reverse every paid split that is not yet reversed with Settlement.ReversePayout for the split's amount. When it is Held, no payout is reversed and the Settlement becomes Reversed, so it is never paid out later. When it is already Reversed, as after every Ticket of the Order was resold, nothing is clawed back and no Settlement is given to Order.CommitRefund. When the Order has no Settlement, nothing is clawed back. Only the paid splits are reversed: the platform fee was never paid out, so it is not recovered from the Organizer, and when a Released Order is refunded — in practice a Dispute that arrives after the release — the platform bears its fee.

#### Scenario: Payout already released

- **WHEN** the Order's Settlement is Released
- **THEN** each paid split is reversed and the Settlement becomes Reversed

#### Scenario: Payout not yet released

- **WHEN** the Order's Settlement is Held
- **THEN** no payout is reversed and the Settlement becomes Reversed

#### Scenario: Settlement given up by resales

- **WHEN** the Order's Settlement was Reversed because every Ticket was resold
- **THEN** nothing is clawed back and the Order is recorded Refunded
