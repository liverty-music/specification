# Spec Delta

## Purpose

TicketSaleUseCase.Get tells anyone looking at an event whether and how its tickets are on sale, without revealing the exact remaining count.

## ADDED Requirements

### Requirement: Sale and its state for an event

Get SHALL take an event and the current time, read its sale with TicketSale.GetByEvent and return:
- the sale start, sale end, price, per-account limit and method;
- the sale's state at that time;
- whether it is LowStock;
- the seller details of the event's Organizer, read with Event.GetOrganizerID and Organizer.Get, which the checkout shows as the 特商法 (Specified Commercial Transactions Act) disclosure.

It SHALL NOT return the quantity, the sold count or the remaining count. It SHALL fail with NotFound when the event has no TicketSale, and also when Event.IsEventPublished reports false for the event, as for a 中止 (cancelled) concert.

#### Scenario: On sale with few left

- **WHEN** a sale of 150 with 15 remaining is read at 12:00 inside its window
- **THEN** it is returned OnSale and LowStock, with its price, the Organizer's seller details and no counts

#### Scenario: Last tickets in checkouts

- **WHEN** the sale's remaining tickets are all held by others
- **THEN** it is returned AllHeld

#### Scenario: Concert cancelled

- **WHEN** the event's concert was cancelled
- **THEN** Get fails with NotFound

#### Scenario: Event without a sale

- **WHEN** the event has no TicketSale
- **THEN** Get fails with NotFound
