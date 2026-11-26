# Spec Delta

## MODIFIED Requirements

### Requirement: Delete removes the user

Delete SHALL load the User through User.Get, failing with NotFound for an unknown User. It SHALL fail with FailedPrecondition, removing nothing, while UserUseCase.ListDeletionBlockers returns any blocker for the User. Otherwise it SHALL start the removal of the User and wait up to 10 seconds for it. The removal SHALL check the blockers again, then remove the User's sign-in identity through User.DeleteIdentity and then the User through User.Delete; the User's Orders, Tickets, LotteryEntries and ResaleListings remain. Delete SHALL succeed when the removal removed the User, fail with FailedPrecondition when the removal found a blocker, and fail with Unavailable when the removal has not ended within the wait. Delete serves the fan removing their own account and an admin removing a fan's account alike.

#### Scenario: Existing user

- **WHEN** Delete is called with a stored User's id and the User holds no Ticket and no Order
- **THEN** the User's identity is removed and the User no longer exists

#### Scenario: Unknown user

- **WHEN** no User has the given id
- **THEN** Delete fails with NotFound

#### Scenario: User holding a ticket

- **WHEN** the User holds an Issued Ticket for an Event whose local date is on or after the current date at the Event's Venue (entity/venue "Current date at a venue")
- **THEN** Delete fails with FailedPrecondition and the User and its identity remain

#### Scenario: User whose concerts are over

- **WHEN** the User's only Ticket is Issued for an Event whose local date has passed, and its Order is Paid
- **THEN** the User is removed and the Order and Ticket remain

#### Scenario: User with a listed resale

- **WHEN** the User has a ResaleListing in status Listed
- **THEN** Delete fails with FailedPrecondition and the User remains

#### Scenario: User with an entry awaiting its draw

- **WHEN** the User has a LotteryEntry in state Entered
- **THEN** Delete fails with FailedPrecondition and the User remains

#### Scenario: User paying for tickets

- **WHEN** the User has a Committed Checkout
- **THEN** Delete fails with FailedPrecondition and the User remains

#### Scenario: User whose win is being charged

- **WHEN** the User has a LotteryEntry in state Won that has no Order yet
- **THEN** Delete fails with FailedPrecondition and the User remains

#### Scenario: User with only refunded purchases

- **WHEN** the User's only Order is Refunded and its Ticket is Voided
- **THEN** the User is removed and the Order and Ticket remain

#### Scenario: User with a resold listing awaiting its refund

- **WHEN** the User's only ResaleListing is Sold and has no refund time
- **THEN** the User is removed, the listing remains, and the refund of the listing still runs without the User

#### Scenario: Retry after the record failed

- **WHEN** a removal removed the identity but ended with User.Delete failing, and Delete is called again for the User
- **THEN** the identity counts as removed and the User no longer exists

## ADDED Requirements

### Requirement: A started removal runs to its end

Once started, a removal SHALL continue whether or not its caller still waits, and SHALL resume after a restart of the platform. A step that fails with Unavailable or DeadlineExceeded SHALL be tried again until 24 hours after the removal started. A User or an identity already gone SHALL count as removed. A removal that ends with another failure, or has not ended after those 24 hours, SHALL be reported to an admin. A removal that finds a blocker SHALL remove nothing and end.

#### Scenario: Record removal fails once

- **WHEN** the identity is removed and User.Delete fails with Unavailable, and succeeds on a later try
- **THEN** the User no longer exists, without anyone calling Delete again

#### Scenario: Identity provider down for a minute

- **WHEN** User.DeleteIdentity fails with Unavailable for 1 minute and then succeeds
- **THEN** Delete fails with Unavailable and the User and its identity are removed afterwards

#### Scenario: Restart in the middle

- **WHEN** the platform restarts after the identity was removed and before the User was
- **THEN** the removal resumes and the User no longer exists

#### Scenario: Failure that a retry cannot fix

- **WHEN** User.Delete fails with Internal
- **THEN** the removal ends and an admin is told

#### Scenario: Still failing after 24 hours

- **WHEN** a step has failed with Unavailable for 24 hours
- **THEN** the removal stops and an admin is told

#### Scenario: Blocker appears before the removal

- **WHEN** the User gains a blocker after Delete's check and before the removal's check
- **THEN** Delete fails with FailedPrecondition and the User and its identity remain

#### Scenario: Two deletions of one User

- **WHEN** two removals of the same User run
- **THEN** the User is removed once and neither is reported to an admin
