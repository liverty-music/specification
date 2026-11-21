## ADDED Requirements

### Requirement: A refused card authorization is explained

The screen SHALL call ResaleEntryService.AuthorizeCard only with a count from 1 to the event's per-account limit minus the tickets the fan holds; for any other count it SHALL return to the count step, say the per-account limit and send nothing. When AuthorizeCard fails with InvalidArgument, the screen SHALL return to the personal details step with the entered name and phone number and say that they could not be used. When AuthorizeCard fails with FailedPrecondition, the screen SHALL re-read what the fan holds and the stock's resale and say why the application was refused, as it does when the screen opens.

#### Scenario: Name or phone number refused

- **WHEN** a fan holding no ticket for the event chooses 2 tickets with a limit of 4 and AuthorizeCard fails with InvalidArgument
- **THEN** the screen shows the personal details step with the entered name and phone number and says to check them

#### Scenario: Count above the limit is not sent

- **WHEN** the fan holds 3 tickets for the event, the event's per-account limit is 4 and the count to apply for is 2
- **THEN** the screen returns to the count step, says the per-account limit and AuthorizeCard is not called
