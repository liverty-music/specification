# Spec Delta

## ADDED Requirements

### Requirement: Expiry of an authorized card authorization

An authorized CardAuthorization SHALL have an expiry time: the time after which its amount can no longer be charged and the hold on the fan's card is given back by the card issuer. It SHALL be usable to charge only before its expiry time.

#### Scenario: Before expiry
- **WHEN** a card authorization expiring at 12:00 on 30 November is charged on 20 November
- **THEN** the charge is allowed

#### Scenario: After expiry
- **WHEN** the same card authorization is charged at 12:00 on 30 November
- **THEN** it cannot be charged
