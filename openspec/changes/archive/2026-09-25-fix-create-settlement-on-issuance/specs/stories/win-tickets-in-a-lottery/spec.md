# Spec Delta

## MODIFIED Requirements

### Requirement: The Organizer's payout readiness never blocks the sale

Fans SHALL be able to apply, win and receive tickets for an Organizer's lottery whatever the state of the Organizer's payout account; only the Organizer's payout waits until the account is Active, as PayoutSweeperUseCase.ReleaseDueSettlements states.

#### Scenario: Organizer still in identity check

- **WHEN** an Organizer whose payout account is Pending runs a lottery and a fan's application wins
- **THEN** the fan is charged and holds Issued Tickets, while the Organizer's payout stays Held until the account is Active
