## ADDED Requirements

### Requirement: Start or change an entry while the window is open

Start SHALL take a TicketType, the calling fan as user and a ticket count. In this order it SHALL:
- read the TicketType and its sale with TicketType.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition when the sale's method is not Lottery;
- fail with InvalidArgument when the count breaks the LotteryEntry count rule;
- fail with FailedPrecondition when the sale's window is not open at the current time;
- apply the verification gate;
- fail with FailedPrecondition when the count does not fit the TicketType's per-account limit, counting the fan's Issued Tickets for the TicketType's event from Ticket.ListByUserAndEvent;
- call LotteryEntry.GetOrCreateDraft, failing with FailedPrecondition when it reports that the fan already has an Entered, Won or Lost entry for the TicketType;
- when GetOrCreateDraft removed a card authorization from the Draft, release it with CardAuthorization.Release;
- return the Draft.

A failed release SHALL NOT fail the call: Start SHALL still return the changed Draft and report the card authorization it could not release for an admin.

Starting again with the same count SHALL resume the same Draft. Starting again with another count SHALL change the same Draft, which then has no card authorization, so the fan authorizes their card again for the new amount.

#### Scenario: Fan starts an entry within the window
- **WHEN** a fan with no entry and no ticket for the event starts an entry for 2 tickets of an open sale's TicketType
- **THEN** a Draft for 2 tickets is returned and nothing is held on the card

#### Scenario: Fan reloads mid-entry
- **WHEN** the fan starts again with the same count
- **THEN** the same Draft is returned

#### Scenario: Count changed after authorizing
- **WHEN** the fan has a Draft for 2 tickets with a card authorization and starts again for 3 tickets
- **THEN** the card authorization is released and the same Draft is returned for 3 tickets with no card authorization

#### Scenario: Release fails on a count change
- **WHEN** the fan changes the count of a Draft with a card authorization and CardAuthorization.Release fails with Unavailable
- **THEN** Start returns the Draft for the new count with no card authorization, and the card authorization it could not release is reported for an admin

#### Scenario: Window closed
- **WHEN** the fan starts at or after the sale's end time
- **THEN** Start fails with FailedPrecondition and stores nothing

#### Scenario: Count over the limit
- **WHEN** the fan requests more tickets than the TicketType's per-account limit
- **THEN** Start fails with InvalidArgument

#### Scenario: Presale winner reaches the limit
- **WHEN** the fan holds 4 Issued Tickets for the event from a presale and starts an entry for 1 ticket of a general sale TicketType whose per-account limit is 4
- **THEN** Start fails with FailedPrecondition and stores nothing

#### Scenario: Second entry
- **WHEN** the fan already has an Entered, Won or Lost entry for the TicketType
- **THEN** Start fails with FailedPrecondition and stores nothing

## REMOVED Requirements

### Requirement: Start an entry while the window is open
**Reason**: Re-entry after a withdrawal no longer exists, and a count change now releases the Draft's card authorization.
**Migration**: Replaced by "Start or change an entry while the window is open".
