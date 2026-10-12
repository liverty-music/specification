# components/entity/card-authorization/get Specification

## Purpose
Reads a CardAuthorization by its id: its amount, card brand and status with the card authorization secret, and, once it is Captured, the captured payment an Order records; it never charges.

## Requirements

### Requirement: Read a card authorization

CardAuthorization.Get SHALL return the CardAuthorization with the given id, its card authorization secret, which SHALL NOT be stored, and its amount, card brand and status as the payment provider reports them now. It SHALL never charge the card. It SHALL fail with NotFound when no CardAuthorization has the id, and with Unavailable when the payment provider cannot be reached.

#### Scenario: Waiting for card authentication
- **WHEN** a card authorization the fan has not yet authenticated is read
- **THEN** it is returned Pending with its amount and its card authorization secret, so the fan can try again

#### Scenario: Authorized card authorization
- **WHEN** a 16000 yen card authorization the fan authenticated on a Visa card is read
- **THEN** it is returned Authorized, for 16000 yen, with the card brand Visa, and nothing is charged

#### Scenario: Unknown id
- **WHEN** no card authorization has the id
- **THEN** CardAuthorization.Get fails with NotFound

#### Scenario: Payment provider unavailable
- **WHEN** the payment provider cannot be reached
- **THEN** CardAuthorization.Get fails with Unavailable

### Requirement: A captured card authorization gives the payment an Order records

For a Captured CardAuthorization, CardAuthorization.Get SHALL also return the captured payment: the amount actually captured in yen, the payment provider's ID for the payment and for the payment method, and the card brand and last four digits when known. It SHALL never return the card number, security code or expiry. For a CardAuthorization in any other status it SHALL return no captured payment.

#### Scenario: Captured payment
- **WHEN** a captured card authorization of 16000 yen on a Visa card ending 4242 is read
- **THEN** it is returned Captured with a captured payment of 16000 yen, Visa and 4242, and no card number, security code or expiry

#### Scenario: Not captured
- **WHEN** the card authorization is Authorized or Released
- **THEN** it is returned without a captured payment
