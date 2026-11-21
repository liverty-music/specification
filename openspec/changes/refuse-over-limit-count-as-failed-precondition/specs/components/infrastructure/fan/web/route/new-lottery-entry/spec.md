## ADDED Requirements

### Requirement: A refused card authorization is explained

The screen SHALL call LotteryEntryService.AuthorizeCard only with a count from 1 to the event's per-account limit; for any other count it SHALL return to the count step, say the per-account limit and send nothing. When AuthorizeCard fails with InvalidArgument, the screen SHALL return to the 本人確認 step with the entered name and phone number and say that they could not be used. When AuthorizeCard fails with FailedPrecondition, the screen SHALL say that the window has closed when it has, that the fan already has an entry in this sale for this event when they do, that the fan's tickets for the event are of another seat type when they are, that the per-account limit would be exceeded when the tickets the fan holds for the event plus the count exceed it, returning the fan to the count step, and otherwise that the entry was not made and cannot be made now.

#### Scenario: Name or phone number refused

- **WHEN** the window is open, the fan has no entry and holds no tickets for the event, chooses 2 tickets with a limit of 4, and AuthorizeCard fails with InvalidArgument
- **THEN** the screen shows the 本人確認 step with the entered name and phone number and says to check them, not the per-account limit

#### Scenario: Over the limit with held tickets

- **WHEN** the event's per-account limit is 4, the fan holds 3 tickets of the same seat type, chooses 2 tickets and AuthorizeCard fails with FailedPrecondition
- **THEN** the screen returns to the count step and says one account may hold 4 tickets for the event

#### Scenario: Refused for another reason

- **WHEN** the window is open, the fan has no entry and holds no tickets for the event, and AuthorizeCard fails with FailedPrecondition because the concert was cancelled
- **THEN** the screen says the entry was not made and cannot be made now, and does not say the per-account limit

#### Scenario: Count above the limit is not sent

- **WHEN** the count to enter is 5 and the event's per-account limit is 4
- **THEN** the screen says the per-account limit and AuthorizeCard is not called
