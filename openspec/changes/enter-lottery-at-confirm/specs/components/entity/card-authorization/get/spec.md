## MODIFIED Requirements

### Requirement: Read a card authorization

CardAuthorization.Get SHALL return the CardAuthorization with the given id, its card authorization secret, which SHALL NOT be stored, the purchase, user, TicketType, ticket count and referral code it was opened with, and its amount, card brand and status as the payment provider reports them now. It SHALL never charge the card. It SHALL fail with NotFound when no CardAuthorization has the id, and with Unavailable when the payment provider cannot be reached.

#### Scenario: Waiting for card authentication
- **WHEN** a card authorization the fan has not yet authenticated is read
- **THEN** it is returned Pending with its amount and its card authorization secret, so the fan can try again

#### Scenario: Authorized card authorization
- **WHEN** a 16000 yen card authorization the fan authenticated on a Visa card for a lottery entry of 2 tickets is read
- **THEN** it is returned Authorized, for 16000 yen, with the card brand Visa, the fan, the TicketType and the count 2, and nothing is charged

#### Scenario: Unknown id
- **WHEN** no card authorization has the id
- **THEN** CardAuthorization.Get fails with NotFound

#### Scenario: Payment provider unavailable
- **WHEN** the payment provider cannot be reached
- **THEN** CardAuthorization.Get fails with Unavailable
