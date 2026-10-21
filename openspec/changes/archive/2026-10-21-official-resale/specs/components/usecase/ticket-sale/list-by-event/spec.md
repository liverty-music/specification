## MODIFIED Requirements

### Requirement: The event's sales and their ticket types

ListByEvent SHALL take an event and the current time and read its sales with TicketSale.ListByEvent. It SHALL return each sale, ordered by start time, with only its TicketType for that event, a TicketType of a FirstCome sale with its state, whether it is LowStock, whether its resale is open and whether resale is available at that time, with the resale deadline read from the event with Event.Get. It SHALL return an empty list when the event has no sale, and also when Event.IsEventPublished reports false for the event, as for a 中止 (cancelled) concert.

#### Scenario: On sale with few left
- **WHEN** an event whose first-come TicketType of 150 has 15 remaining is read at 12:00 inside the sale's window
- **THEN** the sale is returned with that TicketType OnSale and LowStock, with its price

#### Scenario: Last tickets in checkouts
- **WHEN** the first-come TicketType's remaining tickets are all held by others
- **THEN** it is returned AllHeld

#### Scenario: Sold out with a resale ticket
- **WHEN** the first-come TicketType sold out and one listing is free before the resale deadline
- **THEN** it is returned SoldOut with resale open and resale available

#### Scenario: Sold out, every listing held
- **WHEN** the first-come TicketType sold out and its only listing is held by another fan's Checkout
- **THEN** it is returned SoldOut with resale open and resale not available

#### Scenario: Tour presale seen from one date
- **WHEN** a sale offers TicketTypes for this event and two other events
- **THEN** the sale is returned with only the TicketType for this event

#### Scenario: Presale and general sale
- **WHEN** the event is offered by a presale starting 1 November and a general sale starting 20 November
- **THEN** both are returned, the presale first

#### Scenario: Concert cancelled
- **WHEN** the event's concert was cancelled
- **THEN** an empty list is returned

#### Scenario: Event without a sale
- **WHEN** the event has no TicketSale
- **THEN** an empty list is returned
