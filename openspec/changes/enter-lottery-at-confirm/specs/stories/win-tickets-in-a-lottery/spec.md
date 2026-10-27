## MODIFIED Requirements

### Requirement: A winning fan receives tickets

After an Organizer creates a Lottery TicketSale for a published event with TicketSaleUseCase.Create, a fan SHALL be able to authorize their card for a ticket count of the event's TicketType with LotteryEntryUseCase.AuthorizeCard, complete card authentication and confirm the entry with LotteryEntryUseCase.Confirm while the window is open, and — when their entry wins — find it Won with LotteryEntryUseCase.ListByTicketType within 2 minutes after the window closes and find its Tickets with TicketUseCase.List within 1 more minute.

#### Scenario: Demand within quantity
- **WHEN** a fan enters 2 tickets for a TicketType of 100 tickets priced 8000 yen, and the window closes with fewer than 100 tickets requested
- **THEN** within 2 minutes the fan's entry is Won and 16000 yen is charged, and within 1 more minute the fan holds 2 Issued Tickets for the event, their faces show the fan's full name and phone number, and their ticket journey for the event is Paid

## ADDED Requirements

### Requirement: An entry is made once the card is authenticated

A fan SHALL have an entry only after completing card authentication for it, and SHALL have it then even if the browser closes before the fan's confirmation reaches the platform. A card authorization for a count the fan left before authenticating SHALL hold nothing and make no entry. Only an entry made before the window closes takes part: an authentication whose entry would be made after the end time SHALL be released instead.

#### Scenario: Count changed before confirming
- **WHEN** a fan authorizes their card for 2 tickets, goes back, authorizes it for 3 tickets, completes card authentication and confirms
- **THEN** the fan has one Entered entry, for 3 tickets, and nothing is held on the card for 2 tickets

#### Scenario: Browser closed after card authentication
- **WHEN** a fan completes card authentication and the browser closes before the confirmation reaches the platform
- **THEN** the fan's entry is Entered and takes part in the draw

#### Scenario: Entry made only after the window closed
- **WHEN** a fan completes card authentication 10 seconds before the end time, and neither the fan's confirmation nor the payment provider's notice reaches the platform before the end time
- **THEN** the fan has no entry, the card authorization is released and the fan is never charged

#### Scenario: Card authentication abandoned
- **WHEN** a fan authorizes their card but leaves without completing card authentication, and the window closes
- **THEN** the fan has no entry and is never charged

## REMOVED Requirements

### Requirement: A fan can withdraw before the draw
**Reason**: A fan cannot withdraw a lottery entry, and there is no unconfirmed Draft to release at the draw.
**Migration**: Replaced by "An entry is made once the card is authenticated"; the E2E tests of "Withdraw and enter again" and "Entry left unconfirmed" are replaced by its scenarios.
