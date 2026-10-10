# Spec Delta

## MODIFIED Requirements

### Requirement: Delete and suppress together

DeleteAndSuppress SHALL remove the Event and, with it, its performers, its Concert, its TicketJourneys, and the TicketTypes offered for it with their lottery entries, and SHALL record a SuppressedConcert for the removed Event's Venue, date and start time. Both effects SHALL happen together or not at all. The Event's Series and the Series' TicketSales SHALL remain.

#### Scenario: Concert with fan journeys
- **WHEN** a Concert that fans track in TicketJourneys is deleted
- **THEN** the Event and those TicketJourneys are removed and its slot is suppressed

#### Scenario: Series stays
- **WHEN** one Event of a Series with discovered TicketSales is deleted
- **THEN** the Series and its TicketSales remain
