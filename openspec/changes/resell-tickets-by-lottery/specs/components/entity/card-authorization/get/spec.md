# Spec Delta

## MODIFIED Requirements

### Requirement: Read a card authorization

CardAuthorization.Get SHALL return the CardAuthorization with the given id, its card authorization secret, which SHALL NOT be stored, the purchase, user, TicketSale of a lottery entry, TicketStock, ticket count and referral code it was opened with, its amount, card brand and status as the payment provider reports them now, and, once it is Authorized, its expiry time. It SHALL never charge the card. It SHALL fail with NotFound when no CardAuthorization has the id, and with Unavailable when the payment provider cannot be reached.

#### Scenario: Waiting for card authentication
- **WHEN** a card authorization the fan has not yet authenticated is read
- **THEN** it is returned Pending with its amount and its card authorization secret and without an expiry time, so the fan can try again

#### Scenario: Authorized card authorization
- **WHEN** a 16000 yen card authorization the fan authenticated on a Visa card for a lottery entry of 2 tickets, chargeable until 12:00 on 30 November, is read
- **THEN** it is returned Authorized, for 16000 yen, with the card brand Visa, the fan, the sale, the TicketStock, the count 2 and the expiry time 12:00 on 30 November, and nothing is charged

#### Scenario: Unknown id
- **WHEN** no card authorization has the id
- **THEN** CardAuthorization.Get fails with NotFound

#### Scenario: Payment provider unavailable
- **WHEN** the payment provider cannot be reached
- **THEN** CardAuthorization.Get fails with Unavailable
