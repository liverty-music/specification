# Spec Delta

## Purpose

TicketJourneyUseCase.MarkPaid sets a buyer's ticket journey for an event to Paid once their purchase is recorded, whether the tickets came from a lottery or a checkout.

## ADDED Requirements

### Requirement: Paid after every recorded purchase

MarkPaid SHALL run for each announced TicketPurchased, with its buyer and event. It SHALL set the buyer's TicketJourney for the event to Paid with TicketJourney.Upsert, replacing whatever status the fan had set, and SHALL NOT announce the change as a ticket journey status change. Running it again for the same purchase SHALL leave the journey Paid. When Upsert fails, MarkPaid SHALL fail with that error and is run again.

#### Scenario: Checkout paid

- **WHEN** the purchase of a fan's checkout is announced
- **THEN** the fan's ticket journey for the event is Paid

#### Scenario: Lottery win

- **WHEN** the purchase of a won lottery application is announced
- **THEN** the buyer's ticket journey for the event is Paid

#### Scenario: Update fails

- **WHEN** TicketJourney.Upsert fails
- **THEN** MarkPaid fails and the journey is updated when it runs again
