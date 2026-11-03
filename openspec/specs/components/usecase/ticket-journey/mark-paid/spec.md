# components/usecase/ticket-journey/mark-paid Specification

## Purpose
TicketJourneyUseCase.MarkPaid sets a user's ticket journey for an event to Paid once their purchase is recorded, whether the tickets came from a lottery or a checkout.

## Requirements

### Requirement: Paid after every recorded purchase

MarkPaid SHALL run for each Order announced as paid, with its user and event. It SHALL set the user's TicketJourney for the event to Paid, set by the platform, with TicketJourney.Upsert, replacing whatever status the fan had set. Running it again for the same Order SHALL leave the journey Paid set by the platform. When Upsert fails, MarkPaid SHALL fail with that error and is run again.

#### Scenario: Checkout paid

- **WHEN** the purchase of a fan's checkout is announced
- **THEN** the fan's ticket journey for the event is Paid set by the platform

#### Scenario: Lottery win

- **WHEN** the purchase of a won lottery entry is announced
- **THEN** the Order's user's ticket journey for the event is Paid set by the platform

#### Scenario: Update fails

- **WHEN** TicketJourney.Upsert fails
- **THEN** MarkPaid fails and the journey is updated when it runs again

### Requirement: MarkPaid raises the hype level to match the concert

After recording Paid, MarkPaid SHALL raise the fan's hype level for the concert's artist to the lowest hype level that matches the concert, through Follow.RaiseHype, when all of these hold: the event is a concert (Concert.ListByIDs); the concert has a lowest matching hype level (components/entity/follow); exactly one of the concert's artists is followed by the fan (Follow.ListByUser); and that Follow is raisable to that level. The fan's home comes from User.Get. A failure in any of these steps SHALL NOT fail MarkPaid, and MarkPaid SHALL NOT be run again for it.

#### Scenario: Paid for a distant concert

- **WHEN** the purchase of a fan with home JP-13 is announced for a concert in JP-40, whose proximity is Away, and the fan follows its artist at Nearby set by default
- **THEN** the journey is Paid set by the platform and the Follow is at Away set by inference

#### Scenario: Raising fails

- **WHEN** the journey is recorded Paid and Follow.RaiseHype fails
- **THEN** MarkPaid succeeds and is not run again
