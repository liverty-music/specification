# Spec Delta

## Purpose

ResaleEntryUseCase.Confirm makes a fan's ResaleEntry from their authorized card authorization, whether the fan's screen or the payment provider's authorization notice calls it first.

## ADDED Requirements

### Requirement: An entry is made from an authorized card authorization

Confirm SHALL take a CardAuthorization that carries a TicketStock. It SHALL read it with CardAuthorization.Get and, when it is authorized for the seat type's amount for its count, store the entry with ResaleEntry.Create and return it. When ResaleEntry.Create refuses the entry (resale no longer open, the application no longer fits, or another Entered entry for the event exists), Confirm SHALL release the card authorization and fail with the same error. When the card authorization is not yet authorized, it SHALL fail with FailedPrecondition and change nothing. A second Confirm for the same card authorization SHALL return the existing entry.

#### Scenario: Entry made
- **WHEN** the fan confirms with a card authorization authorized for 10000 yen for 2 tickets
- **THEN** an Entered entry for 2 tickets is returned

#### Scenario: Stock no longer sold out
- **WHEN** a commit was reverted and the stock is no longer sold out when the fan confirms
- **THEN** Confirm releases the card authorization and fails with FailedPrecondition

#### Scenario: Fan and notice both confirm
- **WHEN** the fan's screen and the authorization notice confirm the same card authorization
- **THEN** one entry exists and both calls return it

#### Scenario: Card authentication not finished
- **WHEN** the card authorization is still waiting for card authentication
- **THEN** Confirm fails with FailedPrecondition and nothing is stored
