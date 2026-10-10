# Spec Delta

## MODIFIED Requirements

### Requirement: Delete removes the Organizer and everything recorded for it

Delete SHALL remove, together or not at all:

- the Organizer;
- its first-party Series with their TicketSales, and their Events, with each Event's TicketTypes, lottery entries, ticket journeys and performers;
- the Orders and Tickets for those Events, with their Reversed Settlements;
- the Scanners of those Events, with their Admissions and RejectedScans;
- its Media records and the Series' cover links;
- its Artist associations and its payout-account record.

Fans' follows of the Artists, and every record unrelated to the Organizer, SHALL remain.

#### Scenario: Organizer with a published Series

- **WHEN** Delete runs for a deactivated Organizer with one Series, one Event, a cover Media and one associated Artist
- **THEN** none of the Organizer, Series, Event, Media record or association exists afterwards, and the Artist and its followers remain

#### Scenario: Refunded purchase

- **WHEN** an Event of the Organizer has one Order that is Refunded and the Ticket issued for it
- **THEN** the Order, the Ticket and the Order's Reversed Settlement are removed with the Event
