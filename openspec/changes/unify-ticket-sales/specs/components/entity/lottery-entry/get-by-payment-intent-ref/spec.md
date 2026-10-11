# Spec Delta

## Purpose

Finds the LotteryEntry a card authorization was placed for, so a charge reported by the payment provider can be traced back to it.

## ADDED Requirements

### Requirement: The entry of a card authorization

GetByPaymentIntentRef SHALL return the LotteryEntry whose authorization has the given reference, and SHALL fail with NotFound when there is none.

#### Scenario: Charged win
- **WHEN** the authorization of a Won entry is looked up
- **THEN** that LotteryEntry is returned

#### Scenario: Unknown authorization
- **WHEN** no LotteryEntry has the reference
- **THEN** GetByPaymentIntentRef fails with NotFound
