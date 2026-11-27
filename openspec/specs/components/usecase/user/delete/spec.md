# UserUseCase.Delete

## Purpose

Removes a fan User from the platform, together with the User's sign-in identity, at the fan's own request (`components/adapter/fan/api/rpc/user`) or at an admin's (`components/adapter/admin/api/rpc/user`). No organizer interface exposes it.

## Requirements

### Requirement: Delete removes the user

Delete SHALL load the User through User.Get, failing with NotFound for an unknown User. It SHALL fail with FailedPrecondition, removing nothing, while UserUseCase.ListDeletionBlockers returns any blocker for the User. Otherwise it SHALL start the removal of the User and wait up to 5 seconds for it. The removal SHALL check the blockers again and remove the User through User.Delete, with no blocker created between the check and the removal, and only then remove the User's sign-in identity through User.DeleteIdentity; the User's Orders, Tickets, LotteryEntries and ResaleListings remain. Delete SHALL succeed when the removal has not ended within the wait, because it then runs to its end on its own, and when it ends within the wait having removed the User, even if removing the identity failed. When the removal ends within the wait without removing the User, Delete SHALL fail with the removal's failure: FailedPrecondition for a blocker, otherwise the code of the failed step. It SHALL fail with Unavailable when the removal cannot be started, or when the wait for it cannot be read; a started removal goes on, so a later Delete fails with NotFound once that removal has removed the User. Delete serves the fan removing their own account and an admin removing a fan's account alike.

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

- **WHEN** a removal ended with User.Delete failing, and Delete is called again for the User
- **THEN** the User and its identity are removed

### Requirement: A started removal runs to its end

Once started, a removal SHALL continue whether or not its caller still waits, and SHALL resume after a restart of the platform. A step that fails with Unavailable or DeadlineExceeded SHALL be tried again until 24 hours after the removal started. A User already gone SHALL count as removed, checked before the blockers, and the removal SHALL still remove its identity; an identity already gone SHALL count as removed. A removal that finds a blocker SHALL remove nothing and end. A removal that ends without having removed both the User and its identity, for a blocker, another failure or after those 24 hours, SHALL be reported to an admin.

#### Scenario: Record removal fails once

- **WHEN** User.Delete fails with Unavailable and succeeds on a later try
- **THEN** the User and its identity are removed, without anyone calling Delete again

#### Scenario: Identity removal fails once

- **WHEN** the User is removed and User.DeleteIdentity fails with Unavailable, and succeeds on a later try
- **THEN** the identity is removed, without anyone calling Delete again

#### Scenario: Identity provider down for a minute

- **WHEN** User.DeleteIdentity fails with Unavailable for 1 minute and then succeeds
- **THEN** Delete succeeds after 5 seconds, the User is already removed and the identity is removed afterwards

#### Scenario: Restart in the middle

- **WHEN** the platform restarts after the User was removed and before the identity was
- **THEN** the removal resumes and the identity is removed

#### Scenario: Failure that a retry cannot fix

- **WHEN** User.Delete fails with Internal within the wait
- **THEN** Delete fails with Internal, the User and its identity remain and an admin is told

#### Scenario: Identity that cannot be removed

- **WHEN** the User is removed and User.DeleteIdentity fails with Internal within the wait
- **THEN** Delete succeeds and an admin is told

#### Scenario: Still failing after 24 hours

- **WHEN** a step has failed with Unavailable for 24 hours
- **THEN** the removal stops and an admin is told

#### Scenario: Blocker appears before the removal

- **WHEN** the User gains a blocker after Delete's check and before the removal's check
- **THEN** Delete fails with FailedPrecondition, the User and its identity remain and an admin is told

#### Scenario: Blocker appears before a retry

- **WHEN** User.Delete failed with Unavailable and the User gains a blocker before the next try
- **THEN** the User and its identity remain and an admin is told

#### Scenario: Two removals of one User

- **WHEN** two removals of the same User run
- **THEN** the User and its identity are removed and neither removal is reported to an admin
