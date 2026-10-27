## ADDED Requirements

### Requirement: An entry is made from an authorized card authorization

Confirm SHALL take a card authorization and, when the fan calls it, the calling fan. It SHALL:
- read the card authorization with CardAuthorization.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist, is not for a lottery entry, or is not the calling fan's; other failures are returned unchanged;
- return the entry that holds the card authorization, when one exists (LotteryEntry.GetByCardAuthorizationID), so a repeated Confirm changes nothing;
- fail with FailedPrecondition when the card authorization is Pending, Captured or Released, releasing nothing;
- read its TicketType with TicketType.Get and check that the card authorization confirms the purchase for the TicketType's price times its ticket count;
- make the entry with LotteryEntry.Create from the card authorization's TicketType, user, ticket count and referral code, and return it; when an entry already holds the card authorization, Create returns that entry.

A card authorization that an entry holds SHALL never be released. Confirm SHALL release an Authorized card authorization with CardAuthorization.Release, and then fail, only when it rejects it: when its TicketType no longer exists, when it does not confirm the purchase, or when LotteryEntry.Create fails with AlreadyExists (another entry of the fan) or FailedPrecondition (the sale's end time passed, the TicketType gone). It fails with InvalidArgument when the amount differs, and with FailedPrecondition otherwise. When the release fails, Confirm SHALL return that failure instead, so the rejection is tried again. No money is captured at entry.

#### Scenario: Fan confirms
- **WHEN** a fan confirms their Authorized 16000 yen card authorization for 2 tickets at 8000 yen
- **THEN** an Entered entry for 2 tickets with that card authorization is made and returned, and nothing is charged

#### Scenario: Confirmed twice
- **WHEN** Confirm runs again for a card authorization that already holds an entry
- **THEN** that entry is returned unchanged

#### Scenario: Fan and notice at the same time
- **WHEN** the fan's Confirm and the payment provider's notice run at the same time for one card authorization, just before the end time
- **THEN** one entry is made, both return it, and the card authorization is not released

#### Scenario: Card authentication not completed
- **WHEN** the card authorization is still Pending
- **THEN** Confirm fails with FailedPrecondition, no entry is made and nothing is released

#### Scenario: American Express card
- **WHEN** the Authorized card authorization is on an American Express card
- **THEN** it is released, Confirm fails with FailedPrecondition and no entry is made

#### Scenario: Amount differs
- **WHEN** the Authorized card authorization is for 8000 yen and the TicketType's price times its count is 16000 yen
- **THEN** it is released, Confirm fails with InvalidArgument and no entry is made

#### Scenario: Second entry
- **WHEN** the fan already has an entry for the TicketType with another card authorization
- **THEN** this card authorization is released, Confirm fails with FailedPrecondition and the first entry is unchanged

#### Scenario: After the end time
- **WHEN** Confirm runs for an Authorized card authorization that no entry holds, after the sale's end time
- **THEN** the card authorization is released, Confirm fails with FailedPrecondition and no entry is made

#### Scenario: TicketType gone
- **WHEN** the card authorization's TicketType was deleted with its event
- **THEN** the card authorization is released, Confirm fails with FailedPrecondition and no entry is made

#### Scenario: Release fails
- **WHEN** Confirm rejects an Authorized card authorization and CardAuthorization.Release fails with Unavailable
- **THEN** Confirm fails with Unavailable and no entry is made

#### Scenario: Someone else's card authorization
- **WHEN** a fan confirms a card authorization opened for another fan, which holds that fan's entry
- **THEN** Confirm fails with PermissionDenied and returns no entry

### Requirement: Card authentication completed without the fan

Confirm SHALL also run, without a calling fan, when the payment provider reports that a card authorization became Authorized, so a fan who closed the browser after card authentication still has their entry. A card authorization for a Checkout SHALL then be left as it is, and Confirm SHALL succeed without effect.

#### Scenario: Browser closed after card authentication
- **WHEN** a fan completes card authentication and closes the browser before their Confirm call, and the payment provider reports the card authorization Authorized
- **THEN** the entry is made with that card authorization

#### Scenario: Checkout's card authorization reported
- **WHEN** the payment provider reports a Checkout's card authorization Authorized
- **THEN** nothing changes

## REMOVED Requirements

### Requirement: Confirm one's own draft once its card is authorized
**Reason**: There is no Draft; the entry is made from the card authorization.
**Migration**: Replaced by "An entry is made from an authorized card authorization".
