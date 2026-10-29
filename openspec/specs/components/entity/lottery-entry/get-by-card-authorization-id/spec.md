# components/entity/lottery-entry/get-by-card-authorization-id Specification

## Purpose
Finds the LotteryEntry a card authorization was opened for, so a charge reported by the payment provider can be traced back to it.

## Requirements

### Requirement: The entry of a card authorization

GetByCardAuthorizationID SHALL return the LotteryEntry whose Order's card authorization has the given id, and SHALL fail with NotFound when there is none.

#### Scenario: Charged win
- **WHEN** the card authorization of a Won entry's Order is looked up
- **THEN** that LotteryEntry is returned

#### Scenario: Unknown card authorization
- **WHEN** no LotteryEntry's Order has a card authorization with the id
- **THEN** GetByCardAuthorizationID fails with NotFound
