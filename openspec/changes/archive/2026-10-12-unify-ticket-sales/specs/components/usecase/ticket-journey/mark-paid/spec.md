# Spec Delta

## MODIFIED Requirements

### Requirement: Paid after every recorded purchase

MarkPaid SHALL run for each Order announced as paid, with its user and event. It SHALL set the user's TicketJourney for the event to Paid with TicketJourney.Upsert, replacing whatever status the fan had set, and SHALL NOT announce the change as a ticket journey status change. Running it again for the same Order SHALL leave the journey Paid. When Upsert fails, MarkPaid SHALL fail with that error and is run again.

#### Scenario: Checkout paid

- **WHEN** the purchase of a fan's checkout is announced
- **THEN** the fan's ticket journey for the event is Paid

#### Scenario: Lottery win

- **WHEN** the purchase of a won lottery entry is announced
- **THEN** the Order's user's ticket journey for the event is Paid

#### Scenario: Update fails

- **WHEN** TicketJourney.Upsert fails
- **THEN** MarkPaid fails and the journey is updated when it runs again
