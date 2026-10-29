# Spec Delta

## MODIFIED Requirements

### Requirement: The entry of a card authorization

GetByCardAuthorizationID SHALL return the LotteryEntry whose Order's card authorization has the given id, and SHALL fail with NotFound when there is none.

#### Scenario: Charged win
- **WHEN** the card authorization of a Won entry's Order is looked up
- **THEN** that LotteryEntry is returned

#### Scenario: Unknown card authorization
- **WHEN** no LotteryEntry's Order has a card authorization with the id
- **THEN** GetByCardAuthorizationID fails with NotFound
