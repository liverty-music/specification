# Spec Delta

## Purpose

Finds the lottery application a card authorization was placed for, so a charge reported by the payment provider can be traced back to it.

## ADDED Requirements

### Requirement: The application of a card authorization

GetByPaymentIntentRef SHALL return the TicketApplication whose card authorization has the given reference, and SHALL fail with NotFound when there is none.

#### Scenario: Charged win

- **WHEN** the authorization of a won application is looked up
- **THEN** that TicketApplication is returned

#### Scenario: Unknown authorization

- **WHEN** no TicketApplication has the reference
- **THEN** GetByPaymentIntentRef fails with NotFound
